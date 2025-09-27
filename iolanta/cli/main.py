import locale
import logging
import sys
from pathlib import Path
from typing import Annotated

import loguru
import platformdirs
from documented import DocumentedError
from rdflib import Literal, URIRef
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from typer import Argument, Exit, Option, Typer
from yarl import URL

from iolanta.cli.models import LogLevel
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode

DEFAULT_LANGUAGE = locale.getlocale()[0].split('_')[0]


console = Console()


app = Typer(
    no_args_is_help=True,
)


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


def decode_datatype(datatype: str) -> URIRef:
    if datatype.startswith('http'):
        return URIRef(datatype)

    return URIRef(f'https://iolanta.tech/datatypes/{datatype}')


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

    # Get the level name first
    level_name = {
        logging.DEBUG: 'DEBUG',
        logging.INFO: 'INFO', 
        logging.WARNING: 'WARNING',
        logging.ERROR: 'ERROR',
    }[level]
    
    # Configure global loguru logger BEFORE creating Iolanta instance
    loguru.logger.remove()
    loguru.logger.add(
        log_file_path,
        level=level_name,
        format='{time} {level} {message}',
        enqueue=True,
    )
    loguru.logger.add(
        sys.stderr,
        level=level_name,
        format='{time} | {level:<8} | {name}:{function}:{line} - {message}',
    )
    loguru.logger.level(level_name)
    
    # Use the global logger
    logger = loguru.logger
    
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
            as_datatype=decode_datatype(as_datatype),
        )

    except DocumentedError as documented_error:
        if level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(
            Markdown(
                str(documented_error),
                justify='left',
            ),
        )
        raise Exit(1)

    except Exception as err:
        if iolanta.logger.level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(str(err))
        raise Exit(1)

    else:
        # FIXME: An intermediary Literal can be used to dispatch rendering.
        match renderable:
            case Table() as table:
                console.print(table)

            case unknown:
                print(unknown)
