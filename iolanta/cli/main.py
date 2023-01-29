from pathlib import Path
import logging
from typing import Optional

from rdflib import URIRef
from rich.console import Console
from rich.table import Table
from typer import Argument, Context, Option, Typer, echo
from urlpath import URL

from iolanta.conversions import url_to_path
from iolanta.graph_providers.find import (
    construct_graph_from_installed_providers,
)
from iolanta.iolanta import Iolanta
from iolanta.models import QueryResultsFormat
from iolanta.renderer import render
from iolanta.shortcuts import construct_root_loader
from iolanta.cli.formatters.choose import cli_print

app = Typer(no_args_is_help=True)


logger = logging.getLogger(__name__)


@app.callback()
def callback(
    context: Context,
    graph: Optional[str] = None,
    log_level: str = 'info',
    source: Optional[str] = Option(None, '--from'),
):
    logger.setLevel(
        {
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }[log_level],
    )

    if graph is None:
        graph = construct_graph_from_installed_providers()   # type: ignore

        if graph is not None:
            logger.info('Using graph from provider.')   # type: ignore
            context.obj = Iolanta(
                loader=construct_root_loader(),
                logger=logger,
                graph=graph,
            )
        else:
            logger.info('Using an in-memory transient graph.')
            context.obj = Iolanta(
                logger=logger,
                loader=construct_root_loader(),
            )

    else:
        url = URL(graph)
        if url.scheme == 'file+shelve':
            raise NotImplementedError('Graph plugins not yet implemented.')

            path = url_to_path(url)
            logger.info(f'Loading pickled graph from `{path}`')
            context.obj = Iolanta(
                loader=construct_root_loader(),
                graph=load_graph(path),
                logger=logger,
            )

        else:
            raise ValueError(f'Unknown path for a graph: {url}')

    if source is not None:
        context.obj.add(Path(source))


@app.command(name='render')
def render_command(
    context: Context,
    url: str,
    environment: str = Option(
        'https://iolanta.tech/cli',
        '--as',
    ),
):
    """Render a given URL."""
    iolanta: Iolanta = context.obj

    if ':' not in url:
        url = f'local:{url}'

    node = iolanta.expand_qname(url)

    Console().print(
        render(
            node=node,
            iolanta=iolanta,
            environments=[
                iolanta.expand_qname(environment),
            ],
        ),
    )


@app.command()
def namespaces(
    context: Context,
):
    """Registered namespaces."""
    iolanta: Iolanta = context.obj

    table = Table(
        'Namespace',
        'URL',
        show_header=True,
        header_style='bold magenta',
    )

    for namespace, url in iolanta.graph.namespaces():   # type: ignore
        table.add_row(namespace, url)

    Console().print(table)


@app.command()
def query(
    context: Context,
    fmt: QueryResultsFormat = Option(
        default=QueryResultsFormat.PRETTY,
        metavar='format',
    ),
    query_text: Optional[str] = Argument(
        None,
        metavar='query',
        help='SPARQL query text. Will be read from stdin if empty.',
    ),
    use_qnames: bool = Option(
        default=True,
        help='Collapse URLs into QNames.',
    ),
):
    """Query Iolanta graph with SPARQL."""
    iolanta: Iolanta = context.obj

    cli_print(
        query_result=iolanta.query(query_text),
        output_format=fmt,
        display_iri_as_qname=use_qnames,
        graph=iolanta.graph,
    )
