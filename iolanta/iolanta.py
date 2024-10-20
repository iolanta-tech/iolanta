import functools
import logging
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
)

import funcy
from rdflib import ConjunctiveGraph, Literal, Namespace, URIRef
from rdflib.term import Node

from iolanta import entry_points
from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.errors import FacetError
from iolanta.facets.facet import Facet
from iolanta.facets.locator import FacetFinder
from iolanta.loaders import Loader
from iolanta.loaders.base import SourceType
from iolanta.loaders.local_directory import merge_contexts
from iolanta.models import (
    ComputedQName,
    LDContext,
    NotLiteralNode,
    Triple,
    TripleTemplate,
)
from iolanta.namespaces import LOCAL
from iolanta.parsers.yaml import YAML
from iolanta.plugin import Plugin
from iolanta.resolvers.python_import import PythonImportResolver
from iolanta.shortcuts import construct_root_loader
from iolanta.stack import Stack
from ldflex import LDFlex


@dataclass
class Iolanta:   # noqa: WPS214
    """Iolanta is a Semantic web browser."""

    language: Literal = Literal('en')

    retrieval_directory: Optional[Path] = None
    graph: ConjunctiveGraph = field(
        default_factory=functools.partial(
            ConjunctiveGraph,
            identifier=LOCAL.term('_inference'),
        ),
    )
    force_plugins: List[Type[Plugin]] = field(default_factory=list)

    facet_resolver: Mapping[URIRef, Type[Facet]] = field(
        default_factory=PythonImportResolver,
    )

    logger: logging.Logger = field(
        default_factory=functools.partial(
            logging.getLogger,
            name='iolanta',
        ),
    )

    sources_added_not_yet_inferred: list[SourceType] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    could_not_retrieve_nodes: Set[Node] = field(
        default_factory=set,
        init=False,
    )

    @cached_property
    def loader(self) -> Loader[SourceType]:
        return construct_root_loader(logger=self.logger)

    @property
    def plugin_classes(self) -> List[Type[Plugin]]:
        """Installed Iolanta plugins."""
        return self.force_plugins or entry_points.plugins('iolanta.plugins')

    @cached_property
    def plugins(self) -> List[Plugin]:
        return [
            plugin_class(iolanta=self)
            for plugin_class in self.plugin_classes
        ]

    @cached_property
    def ldflex(self) -> LDFlex:
        """LDFlex is a wrapper to make SPARQL querying RDF graphs bearable."""
        return LDFlex(self.graph)

    @cached_property
    def namespaces_to_bind(self) -> Dict[str, Namespace]:
        return {
            key: Namespace(value)
            for key, value in self.default_context['@context'].items()
            if (
                isinstance(value, str)
                and not value.startswith('@')
                and not key.startswith('@')
            )
        }

    def add(  # type: ignore
        self,
        source: Any,
        context: Optional[LDContext] = None,
        graph_iri: Optional[URIRef] = None,
    ) -> 'Iolanta':
        """Parse & load information from given URL into the graph."""
        self.logger.info('Adding to graph: %s', source)
        self.sources_added_not_yet_inferred.append(source)

        quads = list(
            self.loader.as_quad_stream(
                source=source,
                iri=graph_iri,
                context=context or self.default_context,
                root_loader=self.loader,
            ),
        )

        quad_tuples = [quad.as_tuple() for quad in quads]
        self.graph.addN(quad_tuples)

        self.bind_namespaces(**self.namespaces_to_bind)

        return self

    def infer(self, closure_class=None) -> 'Iolanta':
        """
        Apply inference.

        TODO Remove this. Or use `reasonable`. Not sure.
        """
        return self

    def bind_namespaces(self, **mappings: Namespace) -> 'Iolanta':
        """Bind namespaces."""
        self.graph.bind(prefix='local', namespace=LOCAL)

        for prefix, namespace in mappings.items():
            self.graph.bind(prefix=prefix, namespace=namespace)

        return self

    @property
    def query(self):
        self.maybe_infer()
        return self.ldflex.query

    @cached_property
    def context_paths(self) -> Iterable[Path]:
        directory = Path(__file__).parent / 'data'

        yield directory / 'context.yaml'

        for plugin in self.plugins:
            if path := plugin.context_path:
                yield path

    @cached_property
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
        for plugin in self.plugins:
            self.add(plugin.data_files)

    def __post_init__(self):
        self.add_files_from_plugins()

    def string_to_node(self, name: str | Node) -> NotLiteralNode:
        """
        Parse a string into a node identifier.

        String might be:
          * a full IRI,
          * a qname,
          * a qname with implied `local:` part,
          * or a blank node identifier.
        """
        if isinstance(name, Node):
            return name

        if ':' in name:
            # This is either a full IRI, a qname, or a blank node identifier.
            try:
                # Trying to interpret this as QName.
                return self.graph.namespace_manager.expand_curie(name)
            except ValueError:
                # If it is not a QName then it is an IRI, let's return it.
                return URIRef(name)

        # This string does not include an ":", so we imply `local:`.
        return URIRef(f'local:{name}')

    def render(
        self,
        node: Node,
        as_datatype: NotLiteralNode,
    ) -> Tuple[Any, Stack]:
        """Find an Iolanta facet for a node and render it."""
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
            return facet.show(), facet.stack

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
