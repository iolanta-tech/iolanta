import functools
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import (  # noqa: WPS235
    Annotated,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
)

import funcy
import loguru
import yaml_ld
from rdflib import ConjunctiveGraph, Literal, Namespace, URIRef
from rdflib.namespace import NamespaceManager
from rdflib.term import Node
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import YAMLLDError

from iolanta import entry_points, namespaces
from iolanta.conversions import path_to_iri
from iolanta.cyberspace.processor import normalize_term
from iolanta.errors import UnresolvedIRI
from iolanta.facets.errors import FacetError
from iolanta.facets.facet import Facet
from iolanta.facets.locator import FacetFinder
from iolanta.loaders.base import SourceType
from iolanta.loaders.local_directory import merge_contexts
from iolanta.models import (
    ComputedQName,
    LDContext,
    NotLiteralNode,
    Triple,
    TripleTemplate,
)
from iolanta.node_to_qname import node_to_qname
from iolanta.parse_quads import parse_quads
from iolanta.parsers.yaml import YAML
from iolanta.plugin import Plugin
from iolanta.resolvers.python_import import PythonImportResolver
from ldflex import LDFlex


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

    sources_added_not_yet_inferred: list[SourceType] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

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

    @property
    def ldflex(self) -> LDFlex:
        """
        Create ldflex instance.

        FIXME: Get rid of it.
        """
        return LDFlex(self.graph)

    @functools.cached_property
    def namespaces_to_bind(self) -> Dict[str, Namespace]:
        """
        Namespaces globally specified for the graph.

        FIXME: Probably get rid of this, I do not know.
        """
        return {
            key: Namespace(value)
            for key, value in self.default_context['@context'].items()  # noqa
            if (
                isinstance(value, str)
                and not value.startswith('@')   # noqa: W503
                and not key.startswith('@')   # noqa: W503
            )
        }

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
        self.sources_added_not_yet_inferred.append(source)

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
                self.logger.warning(f'{source_file} | No data found')
                continue

            quad_tuples = [
                tuple([
                    normalize_term(term) for term in replace(
                        quad,
                        graph=graph,
                    ).as_tuple()
                ])
                for quad in quads
            ]

            self.graph.addN(quad_tuples)

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

    @property
    def query(self):
        """Make a SPARQL query."""
        self.maybe_infer()
        return self.ldflex.query

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

    @functools.cached_property
    def default_context(self) -> LDContext:
        """Construct default context from plugins."""
        context_documents = [
            YAML().as_jsonld_document(path.open('r'))
            for path in self.context_paths
        ]

        for context in context_documents:
            if isinstance(context, list):
                raise ValueError('Context cannot be a list: %s', context)

        return merge_contexts(*context_documents)   # type: ignore

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

    def retrieve_triple(self, triple_template: TripleTemplate) -> Triple:
        """Retrieve remote data to project directory."""
        for plugin in self.plugins:
            # FIXME Parallelization?
            plugin.retrieve_triple(triple_template)

        if not downloaded_files:
            self.could_not_retrieve_nodes.add(node)

        for path in downloaded_files:
            self.add(path)

        return self

    def maybe_infer(self):
        """
        Apply inference lazily.

        Only run inference if there are new files added after last inference.
        """
        if self.sources_added_not_yet_inferred:
            self.infer()

    def find_triple(
        self,
        triple_template: TripleTemplate,
    ) -> Triple | None:
        """Lightweight procedure to find a triple by template."""
        triples = self.graph.triples(
            (triple_template.subject, triple_template.predicate, triple_template.object),
        )

        raw_triple = funcy.first(triples)
        if raw_triple:
            return Triple(*raw_triple)

        return self.retrieve_triple(triple_template)

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
