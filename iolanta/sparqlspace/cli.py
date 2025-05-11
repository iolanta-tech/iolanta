from enum import StrEnum
from typing import Annotated

import rich
from rdflib import Node
from rdflib.query import Result
from rich.table import Table
from typer import Typer, Option

from iolanta.sparqlspace.sparqlspace import SPARQLSpace

app = Typer()


class OutputFormat(StrEnum):
    CSV = 'csv'
    JSON = 'json'
    TABLE = 'table'


def _format_node(node: Node):
    return node


def _format_result(result: Result, output_format: OutputFormat):
    match output_format:
        case OutputFormat.CSV:
            return result.serialize(format='csv').decode()
        case OutputFormat.JSON:
            return result.serialize(format='json').decode()
        case OutputFormat.TABLE:
            table = Table(*result.vars)
            for row in result:
                table.add_row(*[
                    _format_node(node)
                    for node in row
                ])
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
    result = SPARQLSpace().query(query)
    rich.print(
        _format_result(
            result=result,
            output_format=output_format,
        ),
    )
