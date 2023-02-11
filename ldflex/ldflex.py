from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Union

from documented import DocumentedError
from frozendict import frozendict
from pyparsing import ParseException
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult
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


def _format_query_bindings(
    bindings: List[Dict[Variable, Identifier]],
) -> SelectResult:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return SelectResult([
        frozendict({
            str(variable_name): rdf_value
            for variable_name, rdf_value
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
    """

    error: ParseException
    query: str

    @property
    def highlight_code(self):
        """Define lines to highlight."""
        return self.error.lineno


@dataclass
class LDFlex:
    """Fluent interface to a semantic graph."""

    graph: Graph

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
                ldflex.query(
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

        return _format_query_bindings(sparql_result.bindings)

    def update(self, sparql_query: str):
        """Apply the given SPARQL INSERT query."""
        self.graph.update(sparql_query)
