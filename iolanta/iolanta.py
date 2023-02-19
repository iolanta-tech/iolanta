import functools
import logging
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Type, Union

import funcy
import owlrl
from owlrl import OWLRL_Extension
from owlrl.Closure import Core
from rdflib import ConjunctiveGraph, Namespace, URIRef
from rdflib.term import Node

from iolanta import entry_points
from iolanta.errors import InsufficientDataForRender
from iolanta.loaders import Loader
from iolanta.loaders.base import SourceType
from iolanta.loaders.local_directory import merge_contexts
from iolanta.models import LDContext, NotLiteralNode
from iolanta.namespaces import IOLANTA, LOCAL
from iolanta.parsers.yaml import YAML
from iolanta.plugin import Plugin
from iolanta.shortcuts import construct_root_loader
from ldflex import LDFlex


@dataclass
class Iolanta:
    """Iolanta is a Semantic web browser."""

    retrieval_directory: Optional[Path] = None
    graph: ConjunctiveGraph = field(
        default_factory=functools.partial(
            ConjunctiveGraph,
            identifier=LOCAL.term('_inference'),
        ),
    )
    force_plugins: List[Type[Plugin]] = field(default_factory=list)

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

        self.graph.addN(quads)

        self.bind_namespaces(**self.namespaces_to_bind)

        return self

    def infer(self, closure_class: Type[Core] = OWLRL_Extension) -> 'Iolanta':
        """Apply inference."""
        self.logger.info(
            'Inference: %s started...',
            closure_class.__name__,
        )
        owlrl.DeductiveClosure(closure_class).expand(self.graph)
        self.logger.info('Inference: complete.')

        self.sources_added_not_yet_inferred = []

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

    def expand_qname(self, qname: str) -> URIRef:
        try:
            return self.graph.namespace_manager.expand_curie(qname)
        except ValueError:
            return URIRef(qname)

    def render(
        self,
        node: Union[str, Node],
        environments: Optional[Union[str, List[NotLiteralNode]]] = None,
    ) -> Any:
        """Find an Iolanta facet for a node and render it."""
        # FIXME: Convert to a global import
        from iolanta.facet.errors import FacetError
        from iolanta.renderer import Render, resolve_facet

        if isinstance(environments, str):
            environments = [environments]

        if not environments:
            environments = [IOLANTA.html]

        self.logger.info('Environments: %s', environments)

        self.maybe_infer()

        facet_search_attempt = Render(
            ldflex=self.ldflex,
        ).search_for_facet(
            node=node,
            environments=environments,
        )

        facet_class = resolve_facet(
            iri=facet_search_attempt.facet,
        )

        facet = facet_class(
            iri=node,
            iolanta=self,
            environment=facet_search_attempt.environment,
        )

        try:
            return facet.show()

        except InsufficientDataForRender:
            raise

        except Exception as err:
            raise FacetError(
                node=node,
                facet_iri=facet_search_attempt.facet,
                facet_search_attempt=facet_search_attempt,
                error=err,
            ) from err

    def render_with_retrieval(
        self,
        node: Union[str, Node],
        environments: Optional[Union[str, List[NotLiteralNode]]] = None,
    ):
        for attempt_id in reversed(range(100)):
            try:
                return self.render(
                    node=node,
                    environments=environments,
                )

            except InsufficientDataForRender as err:
                if attempt_id == 0:
                    raise ValueError('Too much data to download :(((') from err

                self.retrieve(
                    node=err.node,
                )


    def retrieve(self, node: Node) -> 'Iolanta':
        """Retrieve remote data to project directory."""
        downloaded_files = list(
            funcy.flatten(
                plugin.retrieve(node)
                for plugin
                in self.plugins
            ),
        )

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
