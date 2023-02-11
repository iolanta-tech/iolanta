import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from typer import Argument, Context, Option, Typer

from iolanta.cli.formatters.choose import cli_print
from iolanta.iolanta import Iolanta
from iolanta.models import QueryResultsFormat
from iolanta.renderer import render
from iolanta.shortcuts import construct_root_loader

logger = logging.getLogger(__name__)


def construct_app() -> Typer:
    iolanta = Iolanta(
        logger=logger,
        loader=construct_root_loader(),
    )

    cli = Typer(
        no_args_is_help=True,
        context_settings={
            'obj': iolanta,
        },
    )

    plugins = iolanta.plugins

    for plugin in plugins:
        if (subcommand := plugin.typer_app) is not None:
            cli.add_typer(subcommand)

    return cli


app = construct_app()


@app.callback()
def callback(
    context: Context,
    log_level: str = 'info',
    source: Path = Option(
        Path.cwd,
        '--from',
        help='File or directory to read data from',
        exists=True,
    ),
):
    iolanta: Iolanta = context.obj

    iolanta.logger.setLevel(
        {
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }[log_level],
    )

    iolanta.add(Path(source))


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
