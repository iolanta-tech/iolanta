import locale
import logging
from typing import Annotated

from documented import DocumentedError
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from typer import Argument, Exit, Option, Typer

from iolanta.cli.models import LogLevel
from iolanta.iolanta import Iolanta

DEFAULT_LANGUAGE = locale.getlocale()[0].split('_')[0]


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
def render_command(   # noqa: WPS231, WPS238
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

    iolanta: Iolanta = Iolanta(
        language=language,
    )
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
            as_datatype=iolanta.string_to_node(as_datatype),
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
        if iolanta.logger.level in {logging.DEBUG, logging.INFO}:
            raise

        console.print(str(err))
        raise Exit(1)

    else:
        Console().print(renderable)
