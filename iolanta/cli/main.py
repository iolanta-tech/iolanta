import locale
import logging
from pathlib import Path
from typing import Annotated

import loguru
import platformdirs
from documented import DocumentedError
from rdflib import Literal, URIRef
from rich.console import Console
from rich.markdown import Markdown
from typer import Argument, Exit, Option, Typer
from yarl import URL

from iolanta.cli.models import LogLevel
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode

DEFAULT_LANGUAGE = locale.getlocale()[0].split('_')[0]


console = Console()


def construct_app() -> Typer:
    """
    Construct Typer app.

    FIXME: Remove this function, just create the app on module level.
    """
    iolanta = Iolanta()

    return Typer(
        no_args_is_help=True,
        context_settings={
            'obj': iolanta,
        },
    )


app = construct_app()


def string_to_node(name: str) -> NotLiteralNode:
    """
    Parse a string into a node identifier.

    String might be:
      * a URL,
      * or a local disk path.
    """
    url = URL(name)
    if url.scheme:
        return URIRef(name)

    path = Path(name).absolute()
    return URIRef(f'file://{path}')


@app.command(name='browse')
def render_command(   # noqa: WPS231, WPS238, WPS210, C901
    url: Annotated[str, Argument()],
    as_datatype: Annotated[
        str, Option(
            '--as',
        ),
    ] = 'https://iolanta.tech/cli/interactive',
    language: Annotated[
        str, Option(
            help='Data language to prefer.',
        ),
    ] = DEFAULT_LANGUAGE,
    log_level: LogLevel = LogLevel.ERROR,
):
    """Render a given URL."""
    level = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
    }[log_level]

    log_file_path = platformdirs.user_log_path(
        'iolanta',
        ensure_exists=True,
    ) / 'iolanta.log'

    logger = loguru.logger
    logger.add(
        log_file_path,
        level=level,
        format='{time} {level} {message}',
        enqueue=True,
    )

    node_url = URL(url)
    if node_url.scheme and node_url.scheme != 'file':
        node = URIRef(url)

        iolanta: Iolanta = Iolanta(
            language=Literal(language),
            logger=logger,
        )
    else:
        path = Path(node_url.path).absolute()
        node = URIRef(f'file://{path}')
        iolanta: Iolanta = Iolanta(
            language=Literal(language),
            logger=logger,
            project_root=path,
        )

    try:
        renderable = iolanta.render(
            node=URIRef(node),
            as_datatype=URIRef(as_datatype),
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
        raise Exit(1)

    except Exception as err:
        if level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(str(err))
        raise Exit(1)

    else:
        Console().print(renderable)
