from pathlib import Path

from more_itertools import consume, first
from rdflib import Literal
from rich.table import Table

from iolanta.cli.formatters.pretty import pretty_print_value
from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class SelectResultTableFacet(RichFacet):
    """Render SELECT query results as table."""

    META = META

    def show(self) -> Renderable:
        """Render SelectResult as table."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        query_result = self.this.value

        if not query_result:
            table = Table(show_header=True, header_style="bold magenta")
            return table

        columns = first(query_result).keys()

        table = Table(
            *columns,
            show_header=True,
            header_style="bold magenta",
        )

        consume(
            table.add_row(
                *[
                    str(pretty_print_value(value))
                    for value in row.values()
                ],
            )
            for row in query_result
        )

        return table
