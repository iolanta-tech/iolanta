import itertools
from datetime import date
from typing import Union

from classes import typeclass
from more_itertools import consume, first
from rdflib import BNode, Graph, Literal, URIRef
from rich.console import Console
from rich.table import Table

from iolanta.cli.pretty_print import render_literal_value
from iolanta.models import ComputedQName
from ldflex.ldflex import QueryResult, SelectResult


@typeclass
def pretty_print_value(rdflib_value: Union[URIRef, Literal, BNode]) -> str:
    """Pretty print a value for a table in CLI."""


@pretty_print_value.instance(type(None))
def _pretty_print_none(none_value):
    """Format None."""
    return f'∅ {none_value}'


@pretty_print_value.instance(URIRef)
def _pretty_print_value_uri_ref(uriref: URIRef):
    """Format URI Ref."""
    return f'🔗 {uriref}'


@pretty_print_value.instance(ComputedQName)
def _pretty_print_value_uri_ref(qname: ComputedQName):
    """Format QName."""
    return (
        f'🔗 [link={qname.namespace_url}]'
        f'[blue]{qname.namespace_name}[/blue][/link]:'
        f'{qname.term}'
    )


@pretty_print_value.instance(Literal)
def _pretty_print_literal(literal: Literal):
    """Render a literal."""
    rendered_value = render_literal_value(literal.toPython())

    if literal.language:
        formatted_language = {
            'ru': '🇷🇺',
            'en': '🇺🇸',
            'ua': '🇺🇦',
        }[literal.language]

        return f'{formatted_language} {rendered_value}'

    return rendered_value


@pretty_print_value.instance(BNode)
def _pretty_print_bnode(bnode: BNode):
    """Print a blank node."""
    return f'😶 {bnode}'


@typeclass
def pretty_print(query_result: QueryResult):
    """Pretty print query result."""


@pretty_print.instance(SelectResult)
def _pretty_print_select_result(select_result: SelectResult):
    """Print a SPARQL query result in style."""
    if not select_result:
        return

    columns = first(select_result).keys()

    table = Table(
        *columns,
        show_header=True,
        header_style="bold magenta",
    )

    consume(
        itertools.starmap(
            table.add_row,
            [
                map(
                    pretty_print_value,
                    row.values(),
                )
                for row in select_result
            ],
        ),
    )

    Console().print(table)


@pretty_print.instance(Graph)
def _pretty_construct(graph: Graph):
    if not graph:
        return

    table = Table(
        'Subject',
        'Predicate',
        'Object',
        show_header=True,
        header_style="bold magenta",
    )

    consume(
        itertools.starmap(
            table.add_row,
            [
                map(
                    pretty_print_value,
                    triple,
                )
                for triple in graph
            ],
        ),
    )

    Console().print(table)
