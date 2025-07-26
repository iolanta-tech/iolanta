import functools
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import (  # noqa: WPS235
    Annotated,
    Any,
    Iterable,
    List,
    Mapping,
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
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.term import Node
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import YAMLLDError

from iolanta import entry_points, namespaces
from iolanta.conversions import path_to_iri
from iolanta.errors import UnresolvedIRI
from iolanta.facets.errors import FacetError
from iolanta.facets.facet import Facet
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
from iolanta.resolvers.python_import import PythonImportResolver
from iolanta.sparqlspace.processor import normalize_term


class LoggerProtocol(Protocol):
    """
    Abstract Logger interface.

    Unites `loguru` & standard `logging`.
    """

    def info(   # noqa: WPS110
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an INFO message."""

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR message."""

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a WARNING message."""


def _create_default_graph():
    return ConjunctiveGraph(identifier=namespaces.LOCAL.term('_inference'))


@dataclass
class Iolanta:   # noqa: WPS214
    """Iolanta is a Semantic web browser."""

    language: Literal = Literal('en')

    project_root: Annotated[
        Path | None,
        (
            'File or directory the contents of which '
            'Iolanta will automatically load into the graph.'
        ),
    ] = None
    graph: ConjunctiveGraph = field(default_factory=_create_default_graph)
    force_plugins: List[Type[Plugin]] = field(default_factory=list)

    facet_resolver: Mapping[URIRef, Type[Facet]] = field(
        default_factory=PythonImportResolver,
    )

    logger: LoggerProtocol = loguru.logger

    could_not_retrieve_nodes: Set[Node] = field(
        default_factory=set,
        init=False,
    )

    @property
    def plugin_classes(self) -> List[Type[Plugin]]:
        """Installed Iolanta plugins."""
        return self.force_plugins or entry_points.plugins('iolanta.plugins')

    @functools.cached_property
    def plugins(self) -> List[Plugin]:
        """
        Construct a list of installed plugin instances.

        # FIXME: Get rid of those.
        """
        return [
            plugin_class(iolanta=self)
            for plugin_class in self.plugin_classes
        ]

    def query(
        self,
        query_text: str,
        **kwargs: SPARQLQueryArgument,
    ) -> QueryResult:
        """
        Run a SPARQL `SELECT`, `CONSTRUCT`, or `ASK` query.

        Args:
            query_text: The SPARQL text;
            **kwargs: bind variables in the query to values if necessary. For
                example:

                ```python
                iolanta.query(
                    'SELECT ?title WHERE { ?page rdfs:label ?title }',
                    ?page=page_iri,
                )
                ```

        Returns:
            Results of the query:

            - a graph for `CONSTRUCT`,
            - a list of dicts for `SELECT`,
            - or a boolean for `ASK`.
        """
        try:
            sparql_result: SPARQLResult = self.graph.query(
                query_text,
                processor='sparqlspace',
                initBindings=kwargs,
            )
        except ParseException as err:
            raise SPARQLParseException(
                error=err,
                query=query_text,
            ) from err

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
        self.graph = _create_default_graph()   # noqa: WPS601
        self.__post_init__()

    def add(  # noqa: C901, WPS231, WPS210, WPS213
        self,
        source: Path,
        context: Optional[LDContext] = None,
        graph_iri: Optional[URIRef] = None,
    ) -> 'Iolanta':
        """Parse & load information from given URL into the graph."""
        self.logger.info(f'Adding to graph: {source}')

        if not isinstance(source, Path):
            source = Path(source)

        for source_file in list(source.rglob('*')) or [source]:
            if source_file.is_dir():
                continue

            try:  # noqa: WPS225
                ld_rdf = yaml_ld.to_rdf(source_file)
            except ConnectionError as name_resolution_error:
                self.logger.warning(
                    '%s | name resolution error: %s',
                    source_file,
                    str(name_resolution_error),
                )
                continue
            except ParserNotFound as parser_not_found:
                self.logger.error(f'{source} | {parser_not_found}')
                continue
            except YAMLLDError as yaml_ld_error:
                self.logger.error(f'{source} | {yaml_ld_error}')
                continue
            except ValueError as value_error:
                self.logger.error(f'{source} | {value_error}')
                continue

            self.logger.info(f'{source_file} is loaded.')

            graph = path_to_iri(source_file)
            try:
                quads = list(
                    parse_quads(
                        quads_document=ld_rdf,
                        graph=graph,
                        blank_node_prefix=str(source),
                    ),
                )
            except UnresolvedIRI as err:
                raise replace(
                    err,
                    context=None,
                    iri=graph,
                )

            if not quads:
                self.logger.info(f'{source_file} | No data found')
                continue

            self.graph.addN(quads)

        return self

    def infer(self, closure_class=None) -> 'Iolanta':
        """
        Apply inference.

        TODO Remove this. Or use `reasonable`. Not sure.
        """
        return self

    def bind_namespaces(self):
        """Bind namespaces."""
        self.graph.namespace_manager = NamespaceManager(
            self.graph,
            bind_namespaces='none',
        )
        self.graph.bind(prefix='local', namespace=namespaces.LOCAL)
        self.graph.bind(prefix='iolanta', namespace=namespaces.IOLANTA)
        self.graph.bind(prefix='rdf', namespace=namespaces.RDF)
        self.graph.bind(prefix='rdfs', namespace=namespaces.RDFS)
        self.graph.bind(prefix='owl', namespace=namespaces.OWL)
        self.graph.bind(prefix='foaf', namespace=namespaces.FOAF)
        self.graph.bind(prefix='schema', namespace=namespaces.SDO)
        self.graph.bind(prefix='vann', namespace=namespaces.VANN)
        self.graph.bind(prefix='np', namespace=namespaces.NP)
        self.graph.bind(prefix='dcterms', namespace=namespaces.DCTERMS)
        self.graph.bind(prefix='rdfg', namespace=namespaces.RDFG)

    @functools.cached_property
    def context_paths(self) -> Iterable[Path]:
        """
        Compile list of context files.

        FIXME: Get rid of those.
        """
        directory = Path(__file__).parent / 'data'

        yield directory / 'context.yaml'

        for plugin in self.plugins:
            if path := plugin.context_path:
                yield path

    def add_files_from_plugins(self):
        """
        Load files from plugins.

        FIXME: Get rid of plugins.
        """
        for plugin in self.plugins:
            try:
                self.add(plugin.data_files)
            except Exception as error:
                self.logger.error(
                    f'Cannot load {plugin} plugin data files: {error}',
                )

    def __post_init__(self):
        """
        Load stuff from plugins.

        FIXME: Get rid of plugins.
        """
        self.bind_namespaces()
        self.add_files_from_plugins()
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
                f'Please provide the datatype to render {node} as.',
            )

        if isinstance(as_datatype, list):
            raise NotImplementedError('Got a list for as_datatype :(')

        found = FacetFinder(
            iolanta=self,
            node=node,
            as_datatype=as_datatype,
        ).facet_and_output_datatype

        facet_class = self.facet_resolver[found['facet']]

        facet = facet_class(
            iri=node,
            iolanta=self,
            as_datatype=found['output_datatype'],
        )

        try:
            return facet.show()

        except Exception as err:
            raise FacetError(
                node=node,
                facet_iri=found['facet'],
                error=err,
            ) from err

    def render_all(
        self,
        node: Node,
        as_datatype: NotLiteralNode,
    ) -> Iterable[Any]:
        """Find all possible Iolanta facets for a node and render them."""
        choices = list(
            FacetFinder(
                iolanta=self,
                node=node,
                as_datatype=as_datatype,
            ).choices(),
        )

        pairs = [
            (self.facet_resolver[row['facet']], row['output_datatype'])
            for row in choices
        ]

        facet_instances = [
            facet_class(
                iri=node,
                iolanta=self,
                as_datatype=output_datatype,
            )
            for facet_class, output_datatype in pairs
        ]

        for facet in facet_instances:
            try:
                yield facet.show()
            except Exception as err:
                raise FacetError(
                    node=node,
                    facet_iri=None,
                    error=err,
                ) from err

    def node_as_qname(self, node: Node):
        """
        Render node as a QName if possible.

        Return the node as is, if it is not.
        """
        qname = node_to_qname(node, self.graph)
        return f'{qname.namespace_name}:{qname.term}' if isinstance(
            qname,
            ComputedQName,
        ) else node
