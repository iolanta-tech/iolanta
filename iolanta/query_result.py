from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Union

from documented import DocumentedError
from frozendict import frozendict
from pyparsing import ParseException
from rdflib import Graph
from rdflib.term import Identifier, Node, Variable

SelectRow = Mapping[str, Node]


class SelectResult(List[SelectRow]):
    """Result of a SPARQL SELECT."""

    @property
    def first(self) -> Optional[SelectRow]:
        """Return first element of the list."""
        return self[0] if self else None


SPARQLQueryArgument = Optional[Union[Node, str, int, float]]


QueryResult = Union[
    SelectResult,   # SELECT
    Graph,          # CONSTRUCT
    bool,           # ASK
]


def format_query_bindings(
    bindings: List[Dict[Variable, Identifier]],
) -> SelectResult:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return SelectResult([
        frozendict({
            str(variable_name): rdf_value
            for variable_name, rdf_value   # noqa: WPS361
            in row.items()
        })
        for row in bindings
    ])


@dataclass
class SPARQLParseException(DocumentedError):
    """
    SPARQL query is invalid.

    Error:

    ```
    {self.error}
    ```

    Query:
    ```sparql hl_lines="{self.highlight_code}"
    {self.query}
    ```
    """  # noqa: D412

    error: ParseException
    query: str

    @property
    def highlight_code(self):
        """Define lines to highlight."""
        return self.error.lineno
