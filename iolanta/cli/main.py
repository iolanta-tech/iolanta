import logging
from pathlib import Path
from typing import Annotated, Optional

import typer
from documented import DocumentedError
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.table import Table
from textual.logging import TextualHandler
from typer import Argument, Context, Option, Typer

from iolanta.cli.formatters.choose import cli_print
from iolanta.cli.models import LogLevel
from iolanta.iolanta import Iolanta
from iolanta.models import QueryResultsFormat

logger = logging.getLogger('iolanta')
console = Console()


def construct_app() -> Typer:
    iolanta = Iolanta(logger=logger)

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


@app.command(name='browse')
def render_command(
    url: Annotated[str, Argument()],
    environment: str = Option(
        'https://iolanta.tech/cli/interactive',
        '--as',
    ),
    log_level: LogLevel = LogLevel.ERROR,
):
    """Render a given URL."""
    level = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
    }[log_level]

    iolanta: Iolanta = Iolanta()
    iolanta.logger.level = level

    logging.basicConfig(
        level=level,
        format='%(message)s',
        datefmt="[%X]",
        handlers=[RichHandler()],
        force=True,
    )

    node = iolanta.string_to_node(url)

    try:
        renderable, stack = iolanta.render(
            node=node,
            environments=[
                iolanta.string_to_node(environment),
            ],
        )

    except DocumentedError as documented_error:
        if iolanta.logger.level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(
            Markdown(
                str(documented_error),
                justify='left',
            ),
        )
        raise typer.Exit(1)

    except Exception as err:
        if iolanta.logger.level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(str(err))
        raise typer.Exit(1)

    else:
        Console().print(renderable)
