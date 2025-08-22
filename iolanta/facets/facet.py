import inspect
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, Iterable, Optional, TypeVar, Union

from rdflib.term import BNode, Literal, Node, URIRef

from iolanta.models import NotLiteralNode, Triple, TripleTemplate
from iolanta.query_result import QueryResult, SPARQLQueryArgument

FacetOutput = TypeVar('FacetOutput')


@dataclass
class Facet(Generic[FacetOutput]):
    """Base facet class."""

    this: Node
    iolanta: 'iolanta.Iolanta' = field(repr=False)
    as_datatype: Optional[NotLiteralNode] = None

    @property
    def stored_queries_path(self) -> Path:
        """Construct directory for stored queries for this facet."""
        return Path(inspect.getfile(self.__class__)).parent / 'sparql'

    def query(
        self,
        query_text: str,
        **kwargs: SPARQLQueryArgument,
    ) -> QueryResult:
        """SPARQL query."""
        return self.iolanta.query(
            query_text=query_text,
            **kwargs,
        )

    def render(
        self,
        node: Union[str, Node],
        as_datatype: NotLiteralNode,
    ) -> Any:
        """Shortcut to render something via iolanta."""
        return self.iolanta.render(
            node=node,
            as_datatype=as_datatype,
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
    def language(self) -> Literal:
        """Preferred language for Iolanta output."""
        return self.iolanta.language

    @cached_property
    def logger(self):
        """Logger."""
        return self.iolanta.logger.bind(facet=self.__class__.__name__)

    def __str__(self):
        """Render."""
        return str(self.show())
