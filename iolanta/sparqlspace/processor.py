# noqa: WPS201, WPS202, WPS402
import dataclasses
import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Iterable, Mapping

import funcy
import loguru
import requests
import yaml_ld
from nanopub import NanopubClient
from rdflib import ConjunctiveGraph, Dataset, Namespace, URIRef, Variable
from rdflib.namespace import RDF as original_RDF
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Processor
from rdflib.term import BNode, Literal, Node
from requests.exceptions import ConnectionError, HTTPError, InvalidSchema
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import NotFound, YAMLLDError
from yarl import URL

from iolanta.errors import UnresolvedIRI
from iolanta.namespaces import (  # noqa: WPS235
    DC,
    DCTERMS,
    FOAF,
    IOLANTA,
    META,
    OWL,
    RDF,
    RDFS,
    VANN,
)
from iolanta.parse_quads import parse_quads
from iolanta.sparqlspace.redirects import apply_redirect

REASONING_ENABLED = True
OWL_REASONING_ENABLED = False

INFERENCE_DIR = Path(__file__).parent / "inference"
INDICES = [  # noqa: WPS407
    URIRef("https://iolanta.tech/visualizations/index.yaml"),
]


def find_retractions_for(nanopublication: URIRef) -> set[URIRef]:
    """Find nanopublications that retract the given one."""
    # See https://github.com/fair-workflows/nanopub/issues/168 for
    # context of this dirty hack.
    use_server = "http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/"

    client = NanopubClient(use_server=use_server)
    client.grlc_urls = [use_server]

    http_url = str(nanopublication).replace(
        "https://",
        "http://",
    )

    try:
        retractions = client.find_retractions_of(http_url)
    except (requests.HTTPError, InvalidSchema):
        return set()

    return {URIRef(retraction) for retraction in retractions}


def _extract_from_mapping(  # noqa: WPS213, WPS231
    algebra: Mapping[str, Any],
) -> Iterable[URIRef | Variable]:
    match algebra.name:  # noqa: WPS242
        case "SelectQuery" | "AskQuery" | "Project" | "Distinct" | "Slice":
            yield from extract_mentioned_urls(algebra["p"])  # noqa: WPS226

        case "BGP":
            yield from [  # noqa: WPS353, WPS221
                term
                for triple in algebra["triples"]
                for term in triple
                if isinstance(term, (URIRef, Variable))
            ]

        case "Filter" | "UnaryNot" | "OrderCondition":
            yield from extract_mentioned_urls(algebra["expr"])  # noqa: WPS204, WPS226

        case "Builtin_EXISTS":
            # Builtin_EXISTS uses 'graph' instead of 'arg'
            yield from extract_mentioned_urls(algebra["graph"])

        case built_in if built_in.startswith("Builtin_"):
            # Some built-ins may not have an 'arg' key
            arg_value = algebra.get("arg")
            if arg_value is not None:
                yield from extract_mentioned_urls(arg_value)

        case "RelationalExpression":
            yield from extract_mentioned_urls(algebra["expr"])
            yield from extract_mentioned_urls(algebra["other"])

        case "LeftJoin":
            yield from extract_mentioned_urls(algebra["p1"])
            yield from extract_mentioned_urls(algebra["p2"])
            yield from extract_mentioned_urls(algebra["expr"])

        case "Join" | "Union":
            yield from extract_mentioned_urls(algebra["p1"])
            yield from extract_mentioned_urls(algebra["p2"])

        case "Extend":
            # Extend is used for BIND expressions - process pattern and expression
            yield from extract_mentioned_urls(algebra["p"])
            yield from extract_mentioned_urls(algebra["expr"])

        case "ConditionalOrExpression" | "ConditionalAndExpression":
            yield from extract_mentioned_urls(algebra["expr"])
            yield from extract_mentioned_urls(algebra["other"])

        case "OrderBy":
            yield from extract_mentioned_urls(algebra["p"])
            yield from extract_mentioned_urls(algebra["expr"])

        case "TrueFilter":
            return

        case "Graph":
            yield from extract_mentioned_urls(algebra["p"])
            yield from extract_mentioned_urls(algebra["term"])

        case unknown_name:
            formatted_keys = ", ".join(algebra.keys())
            loguru.logger.info(
                "Unknown SPARQL expression "
                f"{unknown_name}({formatted_keys}): {algebra}",
            )
            return


def extract_mentioned_urls(
    algebra,
) -> Iterable[URIRef | Variable]:
    """Extract flat triples from parsed SPARQL query."""
    match algebra:
        case Variable() as query_variable:
            yield query_variable

        case URIRef() as uri_ref:
            yield uri_ref

        case dict():
            yield from _extract_from_mapping(algebra)

        case list() as expressions:
            for expression in expressions:
                yield from extract_mentioned_urls(expression)

        case unknown_algebra:
            algebra_type = type(unknown_algebra)
            raise ValueError(
                f"Algebra of unknown type {algebra_type}: {unknown_algebra}",
            )


def normalize_term(term: Node) -> Node:
    """
    Normalize RDF terms.

    This is an exctremely dirty hack to fix a bug in OWL reported here:

    > https://stackoverflow.com/q/78934864/1245471

    TODO This is:
      * A dirty hack;
      * Based on hard code.
    """
    if isinstance(term, URIRef):
        return apply_redirect(term)

    return term


def resolve_variables(
    terms: Iterable[URIRef | Variable],
    bindings: Mapping[str, Node],
):
    """Replace variables with their values."""
    for term in terms:
        match term:
            case URIRef():
                yield term

            case Variable() as query_variable:
                variable_value = bindings.get(str(query_variable))
                if variable_value is not None and isinstance(variable_value, URIRef):
                    yield variable_value


def extract_mentioned_urls_from_query(
    query: Query,
    bindings: dict[str, Node],
    base: str | None,
    namespaces: dict[str, Namespace],
) -> tuple[Query, set[URIRef]]:
    """Extract URLs that a SPARQL query somehow mentions."""
    return query, set(
        resolve_variables(
            extract_mentioned_urls(query.algebra),
            bindings=bindings,
        ),
    )


@dataclasses.dataclass
class Loaded:
    """The data was loaded successfully."""


@dataclasses.dataclass
class Skipped:
    """The data is already in the graph and loading was skipped."""


LoadResult = Loaded | Skipped


def _extract_nanopublication_uris(  # noqa: WPS231
    algebra: CompValue,
) -> Iterable[URIRef]:
    """Extract nanopublications to get retracting information for."""
    match algebra.name:  # noqa: WPS242
        case "SelectQuery" | "AskQuery" | "Project" | "Distinct" | "Graph":
            yield from _extract_nanopublication_uris(algebra["p"])
        case "ConstructQuery":
            # CONSTRUCT queries don't have nanopublication URIs in bindings
            return

        case "Slice":
            yield from _extract_nanopublication_uris(algebra["p"])

        case "BGP":
            for retractor, retracts, retractee in algebra["triples"]:
                if retracts == URIRef(
                    "https://purl.org/nanopub/x/retracts",
                ) and isinstance(retractor, Variable):
                    yield retractee

        case "LeftJoin" | "Join" | "Union":
            yield from _extract_nanopublication_uris(algebra["p1"])
            yield from _extract_nanopublication_uris(algebra["p2"])

        case "Extend":
            # Extend is used for BIND expressions - process the pattern recursively
            yield from _extract_nanopublication_uris(algebra["p"])

        case "Filter" | "OrderBy":
            return

        case unknown_name:
            raise ValueError(
                f"Unknown algebra name: {unknown_name}, content: {algebra}",
            )


def extract_triples(algebra: CompValue) -> Iterable[tuple[Node, Node, Node]]:
    """Extract triples from a SPARQL query algebra instance."""
    if isinstance(algebra, CompValue):
        for key, value in algebra.items():  # noqa: WPS110
            if key == "triples":
                yield from value

            else:
                yield from extract_triples(value)


@dataclasses.dataclass(frozen=True)
class NanopubQueryPlugin:
    """Import additional information from Nanopublications Registry."""

    graph: Dataset

    def __call__(self, query: Query, bindings: dict[str, Any]):
        """Get stuff from Nanopub Registry, if it makes sense."""
        class_uris = resolve_variables(
            set(self._find_classes(query.algebra)),
            bindings,
        )
        for class_uri in class_uris:
            if self._is_from_nanopubs(class_uri):
                self._load_instances(class_uri)

    def _find_classes(self, algebra: CompValue) -> Iterable[URIRef]:
        triples = extract_triples(algebra)
        for _subject, potential_type, potential_class in triples:
            if potential_type == original_RDF.type:
                yield potential_class

    @funcy.retry(errors=requests.HTTPError, tries=3, timeout=3)
    def _load_instances(self, class_uri: URIRef):
        """
        Load instances from Nanopub Registry.

        FIXME: Can we cache this?
        """
        response = requests.post(  # noqa: S113
            "https://query.knowledgepixels.com/repo/full",
            data={
                "query": "CONSTRUCT WHERE { ?instance a <%s> }" % class_uri,
            },
            headers={
                "Accept": "application/ld+json",
            },
        )

        response.raise_for_status()

        self.graph.get_context(BNode()).parse(
            data=response.text,
            format="json-ld",
        )

    def _is_from_nanopubs(self, class_uri: URIRef) -> bool:
        if not isinstance(class_uri, URIRef):
            raise ValueError(f"Not a URIRef: {class_uri}")

        return self.graph.query(  # noqa: WPS462
            """
            ASK WHERE {
                ?_whatever <https://purl.org/nanopub/x/introduces> $class
            }
            """,
            initBindings={
                "class": class_uri,
            },
        ).askAnswer


@dataclasses.dataclass(frozen=True)
class GlobalSPARQLProcessor(Processor):  # noqa: WPS338, WPS214
    """
    Execute SPARQL queries against the whole Linked Data Web, or The Cyberspace.

    When running the queries, we will try to find and to import pieces of LD
    which can be relevant to the query we are executing.
    """

    graph: ConjunctiveGraph
    inference_lock: Lock = dataclasses.field(default_factory=Lock)
    logger: Any = loguru.logger

    def __post_init__(self):
        """Note that we do not presently need OWL inference."""
        self.graph.last_not_inferred_source = None
        self.graph._indices_loaded = False

    def _maybe_load_indices(self):
        if not self.graph._indices_loaded:
            for index in INDICES:
                self.load(index)

            self.graph._indices_loaded = True

    def query(  # noqa: WPS211, WPS210, WPS231, WPS213, C901
        self,
        strOrQuery,
        initBindings=None,
        initNs=None,
        base=None,
        DEBUG=False,
    ):
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """
        self._maybe_load_indices()

        initBindings = initBindings or {}
        initNs = initNs or {}

        if isinstance(strOrQuery, Query):
            query = strOrQuery

        else:
            parse_tree = parseQuery(strOrQuery)
            query = translateQuery(parse_tree, base, initNs)

        # Only extract nanopublications from SELECT/ASK queries, not CONSTRUCT
        if query.algebra.name != "ConstructQuery":
            self.load_retracting_nanopublications_by_query(
                query=query,
                bindings=initBindings,
                base=base,
                namespaces=initNs,
            )

        query, urls = extract_mentioned_urls_from_query(
            query=query,
            bindings=initBindings,
            base=base,
            namespaces=initNs,
        )

        # Filter out inference graph names (they're not URLs to load)
        urls = {url for url in urls if not str(url).startswith("inference:")}

        for url in urls:
            try:
                self.load(url)
            except Exception as err:
                self.logger.exception(f"Failed to load {url}: {err}", url, err)

        # Run inference if there's new data since last inference run
        # (after URLs are loaded so inference can use the loaded data)
        if self.graph.last_not_inferred_source is not None:  # noqa: WPS504
            last_source = self.graph.last_not_inferred_source
            self.logger.debug(
                f"Running inference, last_not_inferred_source: {last_source}"
            )  # noqa: WPS237
            self._run_inference()
        else:
            self.logger.debug("Skipping inference, last_not_inferred_source is None")

        NanopubQueryPlugin(graph=self.graph)(query, bindings=initBindings)

        is_anything_loaded = True
        while is_anything_loaded:
            is_anything_loaded = False

            query_result = evalQuery(self.graph, query, initBindings, base)

            try:
                bindings = list(query_result["bindings"])
            except KeyError:
                # This was probably an ASK query
                return query_result

            for row in bindings:
                break
                for _, maybe_iri in row.items():  # noqa: WPS427
                    if isinstance(maybe_iri, URIRef) and isinstance(
                        self.load(maybe_iri), Loaded
                    ):
                        is_anything_loaded = True  # noqa: WPS220
                        self.logger.info(  # noqa: WPS220
                            "Newly loaded: {uri}",
                            uri=maybe_iri,
                        )

        query_result["bindings"] = bindings
        return query_result

    def _is_loaded(self, uri: URIRef) -> bool:
        """Find out if this URI in the graph already."""
        return (
            funcy.first(
                self.graph.quads(
                    (
                        uri,
                        IOLANTA["last-loaded-time"],
                        None,
                        META,
                    )
                ),
            )
            is not None
        )

    def _mark_as_loaded(self, uri: URIRef):
        self.graph.add(
            (
                uri,
                IOLANTA["last-loaded-time"],
                Literal(datetime.datetime.now()),
                META,
            )
        )

    def _follow_is_visualized_with_links(self, uri: URIRef):
        """Follow `dcterms:isReferencedBy` links."""
        triples = self.graph.triples((uri, DCTERMS.isReferencedBy, None))
        for _, _, visualization in triples:
            if isinstance(visualization, URIRef):
                self.load(visualization)

    def load(  # noqa: C901, WPS210, WPS212, WPS213, WPS231
        self,
        source: URIRef,
    ) -> LoadResult:
        """
        Try to load LD denoted by the given `source`.

        TODO This function is too big, we have to refactor it.
        """
        # Blank nodes cannot be loaded from URLs
        if isinstance(source, BNode):
            return Skipped()

        # Also check if URIRef represents a blank node (can happen if BNode
        # was serialized to string and converted to URIRef)
        if isinstance(source, URIRef) and str(source).startswith("_:"):
            raise ValueError("This is actually a blank node but masked as a URIREF")

        url = URL(source)

        if url.scheme in {"file", "python", "local", "urn", "doi"}:
            # FIXME temporary fix. `yaml-ld` doesn't read `context.*` files and
            #   fails.
            return Skipped()

        if url.fragment:
            # Fragment on an HTML page resolves to that same page. Let us remove
            # this ambiguity, then.
            # TODO: It works differently for JSON-LD documents AFAIK. Need to
            #   double check that.
            url = url.with_fragment(None)
            source = URIRef(str(f"{url}#"))

        self._follow_is_visualized_with_links(source)

        new_source = apply_redirect(source)
        if new_source != source:
            self.logger.info(
                "Rewriting: {source} → {new_source}",
                source=source,
                new_source=new_source,
            )
            return self.load(new_source)

        source_uri = normalize_term(source)
        if self._is_loaded(source_uri):
            return Skipped()

        # FIXME This is definitely inefficient. However, python-yaml-ld caches
        #   the document, so the performance overhead is not super high.
        try:
            resolved_source = yaml_ld.load_document(source)["documentUrl"]
        except NotFound as not_found:
            self.logger.info(f"{not_found.path} | 404 Not Found")
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(str(namespace)):
                    self.load(URIRef(namespace))
                    self.logger.info(
                        "Redirecting %s → namespace %s",
                        not_found.path,
                        namespace,
                    )
                    return Loaded()

            self.logger.info(
                "{path} | Cannot find a matching namespace",
                path=not_found.path,
            )

            self._mark_as_loaded(source_uri)

            return Loaded()

        except Exception as err:
            self.logger.info(f"{source} | Failed: {err}")
            self.graph.add(
                (
                    URIRef(source),
                    RDF.type,
                    IOLANTA["failed"],
                    source_uri,
                )
            )
            self._mark_as_loaded(source_uri)

            return Loaded()

        if resolved_source:
            resolved_source_uri_ref = URIRef(resolved_source)
            if resolved_source_uri_ref != URIRef(source):
                self.graph.add(
                    (
                        source_uri,
                        IOLANTA["redirects-to"],
                        resolved_source_uri_ref,
                    )
                )
                source = resolved_source

        self._mark_as_loaded(source_uri)

        try:  # noqa: WPS225
            ld_rdf = yaml_ld.to_rdf(source)
        except ConnectionError as name_resolution_error:
            self.logger.info(
                "%s | name resolution error: %s",
                source,
                str(name_resolution_error),
            )
            return Loaded()
        except ParserNotFound as parser_not_found:
            self.logger.info(f"{source} | {parser_not_found}")
            return Loaded()
        except YAMLLDError as yaml_ld_error:
            self.logger.error(f"{source} | {yaml_ld_error}")
            return Loaded()
        except HTTPError as http_error:
            self.logger.warning(f"{source} | HTTP error: {http_error}")
            return Loaded()

        try:
            quads = list(
                parse_quads(
                    quads_document=ld_rdf,
                    graph=source_uri,
                    blank_node_prefix=str(source),
                ),
            )
        except UnresolvedIRI as err:
            raise dataclasses.replace(
                err,
                context=None,
                iri=source,
            )

        if not quads:
            self.logger.info("{source} | No data found", source=source)
            return Loaded()

        self.graph.addN(quads)
        self.graph.last_not_inferred_source = source

        into_graphs = ", ".join({quad.graph for quad in quads})
        self.logger.info(
            f"{source} | loaded {len(quads)} triples into graphs: {into_graphs}",
        )

        return Loaded()

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term

    def _run_inference_from_directory(  # noqa: WPS231, WPS220, WPS210
        self,
        inference_dir: Path,
        graph_prefix: str = "inference",
    ):
        """
        Run inference queries from a given inference directory.

        For each SPARQL file in the inference directory:
        1. Truncate the named graph `local:{graph_prefix}-{filename}`
        2. Execute the CONSTRUCT query
        3. Insert the resulting triples into that graph

        Args:
            inference_dir: Directory containing inference SPARQL files
            graph_prefix: Prefix for inference graph names
            return_count: Whether to return the count of inferred triples

        Returns the total number of triples inferred.
        """
        if not inference_dir.exists():
            return 0

        total_inferred = 0
        for inference_file in inference_dir.glob("*.sparql"):
            filename = inference_file.stem  # filename without .sparql extension
            inference_graph = URIRef(f"{graph_prefix}:{filename}")

            # Truncate the inference graph
            context = self.graph.get_context(inference_graph)
            context.remove((None, None, None))

            # Read and execute the CONSTRUCT query
            query_text = inference_file.read_text()
            query_result = self.graph.query(query_text)  # noqa: WPS110

            # CONSTRUCT queries return a SPARQLResult with a graph attribute
            result_graph = (
                query_result.get("graph")
                if isinstance(query_result, dict)
                else query_result.graph
            )
            self.logger.debug(
                f"Inference {filename}: result_graph is {result_graph}, type: {type(result_graph)}"
            )
            if result_graph is not None:  # noqa: WPS504
                inferred_quads = [
                    (s, p, o, inference_graph)  # noqa: WPS111
                    for s, p, o in result_graph  # noqa: WPS111
                ]
                self.logger.debug(
                    f"Inference {filename}: generated {len(inferred_quads)} quads"
                )

                if inferred_quads:
                    self.graph.addN(inferred_quads)  # noqa: WPS220
                    inferred_count = len(inferred_quads)
                    total_inferred += inferred_count
                    self.logger.info(  # noqa: WPS220
                        "Inference {filename}: added {count} triples",
                        filename=filename,
                        count=inferred_count,
                    )
            else:
                self.logger.debug(f"Inference {filename}: result_graph is None")

        return total_inferred

    def _run_inference(self):  # noqa: WPS231, WPS220, WPS210
        """
        Run inference queries from the inference directory.

        For each SPARQL file in the inference directory:
        1. Truncate the named graph `local:inference-{filename}`
        2. Execute the CONSTRUCT query
        3. Insert the resulting triples into that graph
        """
        with self.inference_lock:
            # Run global inference (deprecated, will be removed later)
            self._run_inference_from_directory(INFERENCE_DIR, graph_prefix="inference")

        # Clear the flag after running inference
        self.graph.last_not_inferred_source = None

    def load_retracting_nanopublications_by_query(  # noqa: WPS231
        self,
        query: Query,
        bindings: dict[str, Node],
        base: str | None,
        namespaces: dict[str, Namespace],
    ):
        """
        If the query requires information about retracting nanopubs, load them.

        FIXME: This function presently does nothing because `nanopub` library
          has problems: https://github.com/fair-workflows/nanopub/issues/168

        TODO: Generalize this mechanism to allow for plugins which analyze
          SPARQL queries and load information into the graph based on their
          content.
        """
        nanopublications = list(
            resolve_variables(
                terms=_extract_nanopublication_uris(query.algebra),
                bindings=bindings,
            ),
        )

        for nanopublication in nanopublications:
            retractions = find_retractions_for(nanopublication)
            for retraction in retractions:
                self.load(retraction)
