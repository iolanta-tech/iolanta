from pathlib import Path
from typing import cast

from more_itertools import consume
from rdflib import Graph, Literal
from rich.table import Table

from iolanta.cli.formatters.pretty import pretty_print_value
from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class ConstructResultTableFacet(RichFacet):
    """Render CONSTRUCT query results as table."""

    META = META

    def show(self) -> Renderable:
        """Render Graph (CONSTRUCT result) as table."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        graph = cast(Graph, self.this.value)

        if not graph:
            table = Table(
                'Subject',
                'Predicate',
                'Object',
                show_header=True,
                header_style="bold magenta",
            )
            return table

        table = Table(
            'Subject',
            'Predicate',
            'Object',
            show_header=True,
            header_style="bold magenta",
        )

        consume(
            table.add_row(
                *[
                    str(pretty_print_value(value))
                    for value in triple
                ],
            )
            for triple in graph
        )

        return table
