import inspect
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, Iterable, List, Optional, TypeVar, Union

from rdflib.term import BNode, Literal, Node, URIRef

from iolanta.models import NotLiteralNode, Triple, TripleTemplate
from iolanta.stack import Stack
from ldflex import LDFlex
from ldflex.ldflex import QueryResult, SPARQLQueryArgument

FacetOutput = TypeVar('FacetOutput')


@dataclass
class Facet(Generic[FacetOutput]):
    """Base facet class."""

    iri: NotLiteralNode
    iolanta: 'iolanta.Iolanta' = field(repr=False)
    as_datatype: Optional[NotLiteralNode] = None
    stack_children: List[Stack] = field(default_factory=list, repr=False)

    @property
    def stored_queries_path(self) -> Path:
        """Construct directory for stored queries for this facet."""
        return Path(inspect.getfile(self.__class__)).parent / 'sparql'

    @property
    def ldflex(self) -> LDFlex:
        """Extract LDFLex instance."""
        return self.iolanta.ldflex

    @cached_property
    def uriref(self) -> NotLiteralNode:
        """Format as URIRef."""
        if isinstance(self.iri, BNode):
            return self.iri

        return URIRef(self.iri)

    def query(
        self,
        query_text: str,
        **kwargs: SPARQLQueryArgument,
    ) -> QueryResult:
        """SPARQL query."""
        return self.ldflex.query(
            query_text=query_text,
            **kwargs,
        )

    def render(
        self,
        node: Union[str, Node],
        as_datatype: NotLiteralNode,
    ) -> Any:
        """Shortcut to render something via iolanta."""
        rendered, stack = self.iolanta.render(
            node=node,
            as_datatype=as_datatype,
        )

        self.stack_children.append(stack)

        return rendered

    def render_all(
        self,
        node: Node,
        as_datatype: NotLiteralNode,
    ) -> Iterable[Any]:
        """Render all we can."""
        return self.iolanta.render_all(node=node, as_datatype=as_datatype)

    def stored_query(self, file_name: str, **kwargs: SPARQLQueryArgument):
        """Execute a stored SPARQL query."""
        query_text = (self.stored_queries_path / file_name).read_text()
        return self.query(
            query_text=query_text,
            **kwargs,
        )

    def show(self) -> FacetOutput:
        """Render the facet."""
        raise NotImplementedError()

    @property
    def language(self) -> Literal:
        """Preferred language for Iolanta output."""
        return self.iolanta.language

    @property
    def stack(self):
        """
        Return stack.

        FIXME: I have no idea. Maybe delete this nonsense.
        """
        return Stack(
            node=self.iri,
            facet=self,
            children=self.stack_children,
        )

    def find_triple(
        self,
        triple: TripleTemplate,
    ) -> Triple | None:
        """Lightweight procedure to find a triple by template."""
        return self.iolanta.find_triple(triple_template=triple)

    @cached_property
    def logger(self):
        """Logger."""
        return self.iolanta.logger.bind(facet=self.__class__.__name__)

    def __str__(self):
        """Render."""
        return str(self.show())
