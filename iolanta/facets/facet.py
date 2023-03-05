import inspect
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, List, Optional, TypeVar, Union

from rdflib.term import BNode, Node, URIRef

from iolanta.models import NotLiteralNode
from iolanta.stack import Stack
from ldflex import LDFlex
from ldflex.ldflex import QueryResult, SPARQLQueryArgument

FacetOutput = TypeVar('FacetOutput')


@dataclass
class Facet(Generic[FacetOutput]):
    """Base facet class."""

    iri: NotLiteralNode
    iolanta: 'iolanta.Iolanta' = field(repr=False)
    environment: Optional[URIRef] = None
    stack_children: List[Stack] = field(default_factory=list)

    @property
    def stored_queries_path(self) -> Path:
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
        environments: Optional[Union[str, List[NotLiteralNode]]] = None,
    ) -> Any:
        """Shortcut to render something via iolanta."""
        rendered, stack = self.iolanta.render(
            node=node,
            environments=environments,
        )

        self.stack_children.append(stack)

        return rendered

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
    def language(self):
        # return self.iolanta.language
        return 'en'

    @property
    def stack(self):
        return Stack(
            node=self.iri,
            facet=self,
            children=self.stack_children,
        )

    def __str__(self):
        """Render."""
        return str(self.show())
