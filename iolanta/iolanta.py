import functools
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import (  # noqa: WPS235
    Annotated,
    Any,
    Iterable,
    List,
    Optional,
    Protocol,
    Set,
    Type,
)

import loguru
import yaml_ld
from pyparsing import ParseException
from rdflib import ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.term import Node
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import YAMLLDError

from iolanta import entry_points, namespaces
from iolanta.conversions import path_to_iri
from iolanta.errors import UnresolvedIRI
from iolanta.facets.errors import FacetError
from iolanta.facets.locator import FacetFinder
from iolanta.models import ComputedQName, LDContext, NotLiteralNode
from iolanta.node_to_qname import node_to_qname
from iolanta.parse_quads import parse_quads
from iolanta.plugin import Plugin
from iolanta.query_result import (
    QueryResult,
    SPARQLParseException,
    SPARQLQueryArgument,
    format_query_bindings,
)
from iolanta.resolvers.base import Resolver
from iolanta.resolvers.dispatch import SchemeDispatchResolver
from iolanta.resolvers.pypi import PyPIResolver
from iolanta.resolvers.python_import import PythonImportResolver
from iolanta.sparqlspace.processor import normalize_term  # noqa: WPS201


class LoggerProtocol(Protocol):
    """Abstract Logger interface that unites `loguru` & standard `logging`."""

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:  # noqa: WPS110
        """Log an INFO message."""

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR message."""

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a WARNING message."""


def _create_default_graph():
    return ConjunctiveGraph(identifier=namespaces.LOCAL.term("_inference"))


@dataclass
class Iolanta:  # noqa: WPS214, WPS338
    """Iolanta is a Semantic web browser."""

    language: Literal = Literal("en")

    project_root: Annotated[
        Path | None,
        (
            "File or directory the contents of which "
            "Iolanta will automatically load into the graph."
        ),
    ] = None
    graph: ConjunctiveGraph = field(default_factory=_create_default_graph)
    force_plugins: List[Type[Plugin]] = field(default_factory=list)

    facet_resolver: Resolver = field(
        default_factory=functools.partial(
            SchemeDispatchResolver,
            python=PythonImportResolver,
            pkg=PyPIResolver,
        ),
    )

    logger: LoggerProtocol = loguru.logger

    could_not_retrieve_nodes: Set[Node] = field(
        default_factory=set,
        init=False,
    )

    _facet_inference_needed: bool = field(
        default=False,
        init=False,
    )

    @property
    def plugin_classes(self) -> List[Type[Plugin]]:
        """Installed Iolanta plugins."""
        return self.force_plugins or entry_points.plugins("iolanta.plugins")

    @functools.cached_property
    def plugins(self) -> List[Plugin]:
        """Construct a list of installed plugin instances."""
        return [plugin_class(iolanta=self) for plugin_class in self.plugin_classes]

    def _run_facet_inference(self):
        """Run inference queries from facet inference directories."""
        for facet_class in self.facet_classes:
            inference_path = facet_class.inference_path

            if inference_path is not None:
                facet_name = facet_class.__name__.lower()
                self._run_inference_from_directory(
                    inference_path,
                    graph_prefix=f"facet-{facet_name}",
                )

    def _run_inference_from_directory(  # noqa: WPS210, WPS231
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
        """
        if not inference_dir.exists():
            return

        inference_files = sorted(inference_dir.glob("*.sparql"))

        for inference_file in inference_files:
            filename = inference_file.stem  # filename without .sparql extension
            inference_graph = URIRef(f"{graph_prefix}:{filename}")

            # Truncate the inference graph
            context = self.graph.get_context(inference_graph)
            context.remove((None, None, None))

            # Read and execute the CONSTRUCT query
            query_text = inference_file.read_text()
            try:
                query_result = self.graph.query(query_text)  # noqa: WPS110
            except (SyntaxError, ParseException) as err:
                self.logger.error(
                    "Invalid SPARQL syntax in inference query {filename}: {error}",
                    filename=filename,
                    error=err,
                )
                raise SPARQLParseException(
                    error=err,
                    query=query_text,
                ) from err

            # CONSTRUCT queries return a SPARQLResult with a graph attribute
            result_graph = (
                query_result.get("graph")
                if isinstance(query_result, dict)
                else query_result.graph
            )
            if result_graph is None:
                raise ValueError(
                    f"CONSTRUCT query {filename} returned None result_graph. "
                    f"query_result type: {type(query_result)}, "
                    f"query_result: {query_result}"
                )

            inferred_quads = [
                (s, p, o, inference_graph)  # noqa: WPS111
                for s, p, o in result_graph  # noqa: WPS111
            ]
            self.logger.info(f"Inference {filename}: generated quads: {inferred_quads}")

            if inferred_quads:
                self.graph.addN(inferred_quads)  # noqa: WPS220
                self.logger.info(  # noqa: WPS220
                    "Inference {filename}: added {count} triples",
                    filename=filename,
                    count=len(inferred_quads),
                )

    def query(
        self,
        query_text: str,
        **kwargs: SPARQLQueryArgument,
    ) -> QueryResult:
        """Run a SPARQL `SELECT`, `CONSTRUCT`, or `ASK` query."""
        try:
            sparql_result: SPARQLResult = self.graph.query(
                query_text,
                processor="sparqlspace",
                initBindings=kwargs,
            )
        except SyntaxError as err:
            raise SPARQLParseException(
                error=err,
                query=query_text,
            ) from err

        # Run facet-specific inference if needed
        if self._facet_inference_needed:
            self._run_facet_inference()
            self._facet_inference_needed = False

        if sparql_result.askAnswer is not None:
            return sparql_result.askAnswer

        if sparql_result.graph is not None:
            graph: Graph = sparql_result.graph
            for prefix, namespace in self.graph.namespaces():
                graph.bind(prefix, namespace)

            return graph

        return format_query_bindings(sparql_result.bindings)

    def reset(self):
        """Reset Iolanta graph."""
        self.graph = _create_default_graph()  # noqa: WPS601
        self._facet_inference_needed = False
        self.__post_init__()

    def add(  # noqa: C901, WPS231, WPS210, WPS213
        self,
        source: Path,
        context: Optional[LDContext] = None,
        graph_iri: Optional[URIRef] = None,
    ) -> "Iolanta":
        """Parse & load information from given URL into the graph."""
        self.logger.info(f"Adding to graph: {source}")

        if not isinstance(source, Path):
            source = Path(source)

        for source_file in list(source.rglob("*")) or [source]:
            if source_file.is_dir():
                continue

            try:  # noqa: WPS225
                ld_rdf = yaml_ld.to_rdf(source_file)
            except ConnectionError as name_resolution_error:
                self.logger.warning(
                    "%s | name resolution error: %s",
                    source_file,
                    str(name_resolution_error),
                )
                continue
            except ParserNotFound as parser_not_found:
                self.logger.error(f"{source} | {parser_not_found}")
                continue
            except (YAMLLDError, BadSyntax) as parse_error:
                self.logger.warning("%s | parse error: %s", source_file, parse_error)
                file_iri = path_to_iri(source_file)
                self.graph.addN(
                    [
                        (
                            file_iri,
                            namespaces.IOLANTA["parse-error"],
                            Literal(str(parse_error)),
                            namespaces.META,
                        ),
                    ]
                )
                continue
            except ValueError as value_error:
                self.logger.error(f"{source} | {value_error}")
                continue

            self.logger.info(f"{source_file} is loaded.")

            graph = path_to_iri(source_file)
            try:
                quads = list(
                    parse_quads(
                        quads_document=ld_rdf,
                        graph=graph,
                        blank_node_prefix=str(source_file),
                    ),
                )
            except UnresolvedIRI as err:
                raise replace(
                    err,
                    context=None,
                    iri=graph,
                )

            if not quads:
                self.logger.info(f"{source_file} | No data found")
                continue

            self.graph.addN(quads)
            self._facet_inference_needed = True

        return self

    def infer(self, closure_class=None) -> "Iolanta":
        """Apply inference."""
        return self

    def bind_namespaces(self):  # noqa: WPS213
        """Bind namespaces."""
        self.graph.namespace_manager = NamespaceManager(
            self.graph,
            bind_namespaces="none",
        )
        self.graph.bind(prefix="local", namespace=namespaces.LOCAL)
        self.graph.bind(prefix="iolanta", namespace=namespaces.IOLANTA)
        self.graph.bind(prefix="rdf", namespace=namespaces.RDF)
        self.graph.bind(prefix="rdfs", namespace=namespaces.RDFS)
        self.graph.bind(prefix="owl", namespace=namespaces.OWL)
        self.graph.bind(prefix="foaf", namespace=namespaces.FOAF)
        self.graph.bind(prefix="schema", namespace=namespaces.SDO)
        self.graph.bind(prefix="vann", namespace=namespaces.VANN)
        self.graph.bind(prefix="np", namespace=namespaces.NP)
        self.graph.bind(prefix="dcterms", namespace=namespaces.DCTERMS)
        self.graph.bind(prefix="rdfg", namespace=namespaces.RDFG)

    @functools.cached_property
    def context_paths(self) -> Iterable[Path]:
        """Compile list of context files."""
        directory = Path(__file__).parent / "data"

        yield directory / "context.yaml"

        for plugin in self.plugins:
            if path := plugin.context_path:  # noqa: WPS332
                yield path

    def add_files_from_plugins(self):
        """Load files from plugins."""
        for plugin in self.plugins:
            try:
                self.add(plugin.data_files)
            except Exception as error:
                self.logger.error(
                    f"Cannot load {plugin} plugin data files: {error}",
                )

    @property
    def facet_classes(self):
        """Get all registered facet classes."""
        return entry_points.plugins("iolanta.facets")

    def add_files_from_facets(self):
        """Add files from all registered facets to the graph."""
        for facet_class in self.facet_classes:
            try:
                self.add(facet_class.META)
            except AttributeError:
                pass  # noqa: WPS420

    def __post_init__(self):
        """Initialize after instance creation."""
        self.bind_namespaces()
        self.add_files_from_plugins()
        self.add_files_from_facets()
        if self.project_root:
            self.add(self.project_root)

    def render(
        self,
        node: Node,
        as_datatype: NotLiteralNode,
    ) -> Any:
        """Find an Iolanta facet for a node and render it."""
        node = normalize_term(node)
        if not as_datatype:
            raise ValueError(
                f"Please provide the datatype to render {node} as.",
            )

        if isinstance(as_datatype, list):
            raise NotImplementedError("Got a list for as_datatype :(")

        found = FacetFinder(
            iolanta=self,
            node=node,
            as_datatype=as_datatype,
        ).facet_and_output_datatype

        facet_class = self.facet_resolver.resolve(found["facet"])

        facet = facet_class(
            this=node,
            iolanta=self,
            as_datatype=found["output_datatype"],
        )

        try:
            return facet.show()

        except Exception as err:
            raise FacetError(
                node=node,
                facet_iri=found["facet"],
                error=err,
            ) from err

    def node_as_qname(self, node: Node):
        """Render node as a QName if possible."""
        qname = node_to_qname(node, self.graph)
        return (
            f"{qname.namespace_name}:{qname.term}"
            if isinstance(
                qname,
                ComputedQName,
            )
            else node
        )
