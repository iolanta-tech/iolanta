import inspect
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import List, Optional, TypeVar, Generic

from rdflib.term import BNode, URIRef

from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode
from ldflex import LDFlex
from ldflex.ldflex import QueryResult, SPARQLQueryArgument

FacetOutput = TypeVar('FacetOutput')


@dataclass
class Facet(Generic[FacetOutput]):
    """Base facet class."""

    iri: NotLiteralNode
    iolanta: Iolanta
    environment: Optional[URIRef] = None

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

    def render(self, iri: NotLiteralNode, environments: List[NotLiteralNode]):
        """Shortcut to render something via iolanta."""
        from iolanta import renderer   # Circular import ☹
        return renderer.render(
            node=iri,
            iolanta=self.iolanta,
            environments=environments,
        )

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

    def __str__(self):
        """Render."""
        return str(self.show())
