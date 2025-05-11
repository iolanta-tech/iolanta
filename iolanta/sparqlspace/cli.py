from enum import StrEnum
from typing import Annotated

import rich
from rdflib import Node
from rdflib.query import Result
from rich.table import Table
from typer import Option, Typer

from iolanta.sparqlspace.sparqlspace import SPARQLSpace

app = Typer()


class OutputFormat(StrEnum):
    """Output formats for the query command."""

    CSV = 'csv'      # noqa: WPS115
    JSON = 'json'    # noqa: WPS115
    TABLE = 'table'  # noqa: WPS115


def _format_node(node: Node):
    return node


def _format_result(query_result: Result, output_format: OutputFormat):
    match output_format:
        case OutputFormat.CSV:
            return query_result.serialize(format='csv').decode()

        case OutputFormat.JSON:
            return query_result.serialize(format='json').decode()

        case OutputFormat.TABLE:
            table = Table(*query_result.vars)
            for row in query_result:
                table.add_row(
                    *[
                        _format_node(node)
                        for node in row
                    ],
                )
            return table

    raise NotImplementedError(f'Output format {output_format} not implemented.')


@app.command(name='query')
def query_command(
    query: str,
    output_format: Annotated[
        OutputFormat,
        Option(help='Output format.'),
    ] = OutputFormat.TABLE,
):
    """Execute a SPARQL query."""
    query_result = SPARQLSpace().query(query)
    rich.print(
        _format_result(
            query_result=query_result,
            output_format=output_format,
        ),
    )
