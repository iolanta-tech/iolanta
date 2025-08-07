import dataclasses
import datetime
import re
import time
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Any, Iterable, Mapping

import diskcache
import funcy
import loguru
import platformdirs
import reasonable
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
from requests.exceptions import ConnectionError, InvalidSchema
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
    PROV,
    RDF,
    RDFS,
    VANN,
)
from iolanta.parse_quads import NORMALIZE_TERMS_MAP, parse_quads

REASONING_ENABLED = True
OWL_REASONING_ENABLED = False
INDICES = [
    URIRef('https://iolanta.tech/visualizations/index.yaml'),
]


REDIRECTS = MappingProxyType({
    # FIXME This is presently hardcoded; we need to
    #   - either find a way to resolve these URLs automatically,
    #   - or create a repository of those redirects online.
    'https://purl.org/vocab/vann/': URIRef(
        'https://vocab.org/vann/vann-vocab-20100607.rdf',
    ),
    URIRef(DC): URIRef(DCTERMS),
    URIRef(RDF): URIRef(RDF),
    URIRef(RDFS): URIRef(RDFS),
    URIRef(OWL): URIRef(OWL),

    # This one does not answer via HTTPS :(
    URIRef('https://xmlns.com/foaf/0.1/'): URIRef('http://xmlns.com/foaf/0.1/'),
    URIRef('https://www.nanopub.org/nschema'): URIRef(
        'https://www.nanopub.net/nschema#',
    ),
    URIRef('https://nanopub.org/nschema'): URIRef(
        'https://nanopub.net/nschema#',
    ),
    URIRef(PROV): URIRef('https://www.w3.org/ns/prov-o'),

    # Convert lexvo.org/id URLs to lexvo.org/data URLs
    r'https://lexvo\.org/id/(.+)': r'http://lexvo.org/data/\1',
    r'https://www\.lexinfo\.net/(.+)': r'http://www.lexinfo.net/\1',
})


@diskcache.Cache(
    directory=str(
        platformdirs.user_cache_path(
            appname='iolanta',
        ) / 'find_retractions_for',
    ),
).memoize(expire=datetime.timedelta(days=8).total_seconds())
def find_retractions_for(nanopublication: URIRef) -> set[URIRef]:
    """Find nanopublications that retract the given one."""
    # See https://github.com/fair-workflows/nanopub/issues/168 for
    # context of this dirty hack.
    use_server = 'http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/'

    client = NanopubClient(use_server=use_server)
    client.grlc_urls = [use_server]

    http_url = str(nanopublication).replace(
        'https://',
        'http://',
    )

    try:
        retractions = client.find_retractions_of(http_url)
    except (requests.HTTPError, InvalidSchema):
        return set()

    return {URIRef(retraction) for retraction in retractions}


def _extract_from_mapping(  # noqa: WPS213
    algebra: Mapping[str, Any],
) -> Iterable[URIRef | Variable]:
    match algebra.name:
        case 'SelectQuery' | 'AskQuery' | 'Project' | 'Distinct':
            yield from extract_mentioned_urls(algebra['p'])

        case 'BGP':
            yield from [   # noqa: WPS353, WPS221
                term
                for triple in algebra['triples']
                for term in triple
                if not isinstance(term, Literal)
            ]

        case 'Filter' | 'UnaryNot' | 'OrderCondition':
            yield from extract_mentioned_urls(algebra['expr'])   # noqa: WPS204

        case built_in if built_in.startswith('Builtin_'):
            yield from extract_mentioned_urls(algebra['arg'])

        case 'RelationalExpression':
            yield from extract_mentioned_urls(algebra['expr'])
            yield from extract_mentioned_urls(algebra['other'])

        case 'LeftJoin':
            yield from extract_mentioned_urls(algebra['p1'])
            yield from extract_mentioned_urls(algebra['p2'])
            yield from extract_mentioned_urls(algebra['expr'])

        case 'Join':
            yield from extract_mentioned_urls(algebra['p1'])
            yield from extract_mentioned_urls(algebra['p2'])

        case 'ConditionalOrExpression' | 'ConditionalAndExpression':
            yield from extract_mentioned_urls(algebra['expr'])
            yield from extract_mentioned_urls(algebra['other'])

        case 'OrderBy':
            yield from extract_mentioned_urls(algebra['p'])
            yield from extract_mentioned_urls(algebra['expr'])

        case 'TrueFilter':
            return

        case 'Graph':
            yield from extract_mentioned_urls(algebra['p'])
            yield from extract_mentioned_urls(algebra['term'])

        case unknown_name:
            formatted_keys = ', '.join(algebra.keys())
            loguru.logger.error(
                'Unknown SPARQL expression '
                f'{unknown_name}({formatted_keys}): {algebra}',
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
                f'Algebra of unknown type {algebra_type}: {unknown_algebra}',
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
    if isinstance(term, URIRef) and term.startswith('http://'):
        term = URIRef(re.sub('^http', 'https', term))

    return NORMALIZE_TERMS_MAP.get(term, term)


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
                if (
                    variable_value is not None
                    and isinstance(variable_value, URIRef)
                ):
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


def _extract_nanopublication_uris(
    algebra: CompValue,
) -> Iterable[URIRef]:
    """Extract nanopublications to get retracting information for."""
    match algebra.name:
        case 'SelectQuery' | 'AskQuery' | 'Project' | 'Distinct' | 'Graph':
            yield from _extract_nanopublication_uris(algebra['p'])

        case 'BGP':
            for retractor, retracts, retractee in algebra['triples']:
                if retracts == URIRef(
                    'https://purl.org/nanopub/x/retracts',
                ) and isinstance(retractor, Variable):
                    yield retractee

        case 'LeftJoin' | 'Join':
            yield from _extract_nanopublication_uris(algebra['p1'])
            yield from _extract_nanopublication_uris(algebra['p2'])

        case 'Filter' | 'OrderBy':
            return

        case unknown_name:
            raise ValueError(
                f'Unknown algebra name: {unknown_name}, '
                f'content: {algebra}',
            )


def apply_redirect(source: URIRef) -> URIRef:   # noqa: WPS210
    """
    Rewrite the URL using regex patterns and group substitutions.

    For each pattern in REDIRECTS:
    - If the pattern matches the source URI
    - Replace the source with the destination, substituting any regex groups
    """
    source_str = str(source)

    for pattern, destination in REDIRECTS.items():
        pattern_str = str(pattern)
        destination_str = str(destination)

        match = re.match(pattern_str, source_str)
        if match:
            # Replace any group references in the destination
            # (like \1, \2, etc.)
            redirected_uri = re.sub(
                pattern_str,
                destination_str,
                source_str,
            )
            return URIRef(redirected_uri)

    return source


def extract_triples(algebra: CompValue) -> Iterable[tuple[Node, Node, Node]]:
    """Extract triples from a SPARQL query algebra instance."""
    if isinstance(algebra, CompValue):
        for key, value in algebra.items():  # noqa: WPS110
            if key == 'triples':
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
        response = requests.post(   # noqa: S113
            'https://query.knowledgepixels.com/repo/full',
            data={
                'query': 'CONSTRUCT WHERE { ?instance a <%s> }' % class_uri,
            },
            headers={
                'Accept': 'application/ld+json',
            },
        )

        response.raise_for_status()

        self.graph.get_context(BNode()).parse(
            data=response.text,
            format='json-ld',
        )

    def _is_from_nanopubs(self, class_uri: URIRef) -> bool:
        if not isinstance(class_uri, URIRef):
            raise ValueError(f'Not a URIRef: {class_uri}')

        return self.graph.query(   # noqa: WPS462
            """
            ASK WHERE {
                ?_whatever <https://purl.org/nanopub/x/introduces> $class
            }
            """,
            initBindings={
                'class': class_uri,
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

    def _infer_with_sparql(self):
        """
        Infer triples with SPARQL rules.

        FIXME:
          * Code these rules into SHACL or some other RDF based syntax;
          * Make them available at iolanta.tech/visualizations/ and indexed.
        """
        inference = Path(__file__).parent / 'inference'

        file_names = {
            'wikibase-claim.sparql': URIRef('local:inference-wikibase-claim'),
            'wikibase-statement-property.sparql': URIRef(
                'local:inference-statement-property',
            ),
        }

        for file_name, graph_name in file_names.items():
            start_time = time.time()
            self.graph.update(
                update_object=(inference / file_name).read_text(),
            )
            triple_count = len(self.graph.get_context(graph_name))
            duration = datetime.timedelta(seconds=time.time() - start_time)
            self.logger.info(
                f'{file_name}: {triple_count} triple(s), '
                f'inferred at {duration}',
            )

    def maybe_apply_inference(self):
        """Apply global OWL RL inference if necessary."""
        if not REASONING_ENABLED:
            return

        if self.graph.last_not_inferred_source is None:
            return

        with self.inference_lock:
            self._infer_with_sparql()
            self._infer_with_owl_rl()
            self.logger.info('Inference @ cyberspace: complete.')

            self.graph.last_not_inferred_source = None

    def _infer_with_owl_rl(self):
        if not OWL_REASONING_ENABLED:
            return

        reasoner = reasonable.PyReasoner()
        reasoner.from_graph(self.graph)
        inferred_triples = reasoner.reason()
        inference_graph_name = BNode('_:inference')
        inferred_quads = [
            (*triple, inference_graph_name)
            for triple in inferred_triples
        ]
        self.graph.addN(inferred_quads)

    def _maybe_load_indices(self):
        if not self.graph._indices_loaded:
            for index in INDICES:
                self.load(index)

            self.graph._indices_loaded = True

    def query(   # noqa: WPS211, WPS210, WPS231, C901
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

        for url in urls:
            try:
                self.load(url)
            except Exception as err:
                self.logger.error(f'Failed to load {url}: {err}', url, err)

        NanopubQueryPlugin(graph=self.graph)(query, bindings=initBindings)

        self.maybe_apply_inference()

        is_anything_loaded = True
        while is_anything_loaded:
            is_anything_loaded = False

            query_result = evalQuery(self.graph, query, initBindings, base)

            try:
                bindings = list(query_result['bindings'])
            except KeyError:
                # This was probably an ASK query
                return query_result

            for row in bindings:
                for _, maybe_iri in row.items():
                    if (
                        isinstance(maybe_iri, URIRef)
                        and isinstance(self.load(maybe_iri), Loaded)
                    ):
                        is_anything_loaded = True   # noqa: WPS220
                        self.logger.info(   # noqa: WPS220
                            'Newly loaded: {uri}',
                            uri=maybe_iri,
                        )

        query_result['bindings'] = bindings
        return query_result

    def _is_loaded(self, uri: URIRef) -> bool:
        """Find out if this URI in the graph already."""
        return funcy.first(
            self.graph.quads((
                uri,
                IOLANTA['last-loaded-time'],
                None,
                META,
            )),
        ) is not None

    def _mark_as_loaded(self, uri: URIRef):
        self.graph.add((
            uri,
            IOLANTA['last-loaded-time'],
            Literal(datetime.datetime.now()),
            META,
        ))

    def _follow_is_visualized_with_links(self, uri: URIRef):
        """Follow `dcterms:isReferencedBy` links."""
        self.logger.info(f'Following links for {uri}…')
        triples = self.graph.triples((uri, DCTERMS.isReferencedBy, None))
        for _, _, visualization in triples:
            if isinstance(visualization, URIRef):
                self.load(visualization)
        self.logger.info('Links followed.')

    def load(   # noqa: C901, WPS210, WPS212, WPS213, WPS231
        self,
        source: URIRef,
    ) -> LoadResult:
        """
        Try to load LD denoted by the given `source`.

        TODO This function is too big, we have to refactor it.
        """
        url = URL(source)

        if url.scheme in {'file', 'python', 'local', 'urn', 'doi'}:
            # FIXME temporary fix. `yaml-ld` doesn't read `context.*` files and
            #   fails.
            return Skipped()

        if url.fragment:
            # Fragment on an HTML page resolves to that same page. Let us remove
            # this ambiguity, then.
            # TODO: It works differently for JSON-LD documents AFAIK. Need to
            #   double check that.
            url = url.with_fragment(None)
            source = URIRef(str(f'{url}#'))

        self._follow_is_visualized_with_links(source)

        new_source = apply_redirect(source)
        if new_source != source:
            self.logger.info(
                'Rewriting: {source} → {new_source}',
                source=source,
                new_source=new_source,
            )
            return self.load(new_source)

        source_uri = normalize_term(source)
        if self._is_loaded(source_uri):
            return Skipped()
        else:
            self.logger.info(f'{source_uri} is not loaded yet')

        # FIXME This is definitely inefficient. However, python-yaml-ld caches
        #   the document, so the performance overhead is not super high.
        try:
            _resolved_source = yaml_ld.load_document(source)['documentUrl']
        except NotFound as not_found:
            self.logger.info(f'{not_found.path} | 404 Not Found')
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(str(namespace)):
                    self.load(URIRef(namespace))
                    self.logger.info(
                        'Redirecting %s → namespace %s',
                        not_found.path,
                        namespace,
                    )
                    return Loaded()

            self.logger.info(
                '{path} | Cannot find a matching namespace',
                path=not_found.path,
            )

            self.graph.add((
                source_uri,
                RDF.type,
                IOLANTA['not-found'],
                source_uri,
            ))

            self._mark_as_loaded(source_uri)

            return Loaded()

        except Exception as err:
            self.logger.info(f'{source} | Failed: {err}')
            self.graph.add((
                URIRef(source),
                RDF.type,
                IOLANTA['failed'],
                source_uri,
            ))
            self._mark_as_loaded(source_uri)

            return Loaded()

        if _resolved_source:
            _resolved_source_uri_ref = URIRef(_resolved_source)
            if _resolved_source_uri_ref != URIRef(source):
                self.graph.add((
                    source_uri,
                    IOLANTA['redirects-to'],
                    _resolved_source_uri_ref,
                ))
                source = _resolved_source

        self._mark_as_loaded(source_uri)

        try:  # noqa: WPS225
            ld_rdf = yaml_ld.to_rdf(source)
        except ConnectionError as name_resolution_error:
            self.logger.info(
                '%s | name resolution error: %s',
                source,
                str(name_resolution_error),
            )
            return Loaded()
        except ParserNotFound as parser_not_found:
            self.logger.info(f'{source} | {parser_not_found}')
            return Loaded()
        except YAMLLDError as yaml_ld_error:
            self.logger.error(f'{source} | {yaml_ld_error}')
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
            self.logger.info('{source} | No data found', source=source)
            return Loaded()

        self.graph.addN(quads)
        self.graph.last_not_inferred_source = source

        into_graphs = ', '.join({
            quad.graph
            for quad in quads
        })
        self.logger.info(
            f'{source} | loaded successfully into graphs: {into_graphs}',
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

    def load_retracting_nanopublications_by_query(    # noqa: WPS231
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
