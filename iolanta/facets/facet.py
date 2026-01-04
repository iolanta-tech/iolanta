import inspect
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar, Union

from rdflib.term import Literal, Node

from iolanta.models import NotLiteralNode
from iolanta.query_result import QueryResult, SPARQLQueryArgument

FacetOutput = TypeVar("FacetOutput")


@dataclass
class Facet(Generic[FacetOutput]):  # noqa: WPS214
    """Base facet class."""

    this: Node
    iolanta: "iolanta.Iolanta" = field(repr=False)
    as_datatype: Optional[NotLiteralNode] = None

    def __post_init__(self):
        if not isinstance(self.this, Node):
            facet_name = self.__class__.__name__
            this_type = type(self.this).__name__
            raise ValueError(
                f"Facet {facet_name} received a non-Node as this: {self.this} (type: {this_type})"
            )

    @property
    def stored_queries_path(self) -> Path:
        """Construct directory for stored queries for this facet."""
        return Path(inspect.getfile(self.__class__)).parent / "sparql"

    inference_path: Optional[Path] = None

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
