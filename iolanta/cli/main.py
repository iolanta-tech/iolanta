import locale
import logging
import sys
from pathlib import Path
from typing import Annotated

import loguru
import platformdirs
from documented import DocumentedError
from rdflib import Graph, Literal, URIRef
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from typer import Argument, Exit, Option, Typer
from yarl import URL

from iolanta.cli.models import LogLevel
from iolanta.facets.errors import FacetNotFound
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES
from iolanta.query_result import (
    QueryResult,
    SPARQLParseException,
    SelectResult,
)

DEFAULT_LANGUAGE = locale.getlocale()[0].split("_")[0]


console = Console()


app = Typer(no_args_is_help=True)


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
    return URIRef(f"file://{path}")


def decode_datatype(datatype: str) -> URIRef:
    if datatype.startswith("http"):
        return URIRef(datatype)

    return URIRef(f"https://iolanta.tech/datatypes/{datatype}")


def setup_logging(log_level: LogLevel):
    """Configure and return logger."""
    level = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
    }[log_level]

    log_file_path = (
        platformdirs.user_log_path(
            "iolanta",
            ensure_exists=True,
        )
        / "iolanta.log"
    )

    level_name = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
    }[level]

    loguru.logger.remove()
    loguru.logger.add(
        log_file_path,
        level=level_name,
        format="{time} {level} {message}",
        enqueue=True,
    )
    loguru.logger.add(
        sys.stderr,
        level=level_name,
        format="{time} | {level:<8} | {name}:{function}:{line} - {message}",
    )
    loguru.logger.level(level_name)

    return loguru.logger


def handle_error(
    error: Exception,
    log_level: LogLevel,
    use_markdown: bool = True,
) -> None:
    """
    Handle an error by checking log level and printing appropriately.

    If log level is DEBUG or INFO, re-raise the error.
    Otherwise, print it and exit with code 1.
    """
    level = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
    }[log_level]

    if level in {logging.DEBUG, logging.INFO}:
        raise error

    if use_markdown:
        console.print(
            Markdown(
                str(error),
                justify="left",
            ),
        )
    else:
        console.print(str(error))

    raise Exit(1)


def create_query_node(query_result: QueryResult) -> Literal:
    """
    Create a Literal node from a query result.

    Converts QueryResult (SelectResult, Graph, or bool) into a Literal
    with the appropriate datatype for facet rendering.
    """
    match query_result:
        case SelectResult():
            return Literal(
                query_result,
                datatype=DATATYPES["sparql-select-result"],
            )
        case Graph():
            return Literal(
                query_result,
                datatype=DATATYPES["sparql-construct-result"],
            )
        case bool():
            return Literal(
                query_result,
                datatype=DATATYPES["sparql-ask-result"],
            )


def render_and_return(
    node: Literal | URIRef,
    as_datatype: str,
    language: str = DEFAULT_LANGUAGE,
    log_level: LogLevel = LogLevel.ERROR,
):
    """
    Render a node.

    The node must be either a URIRef (for URLs) or a Literal (for query results).
    """
    logger = setup_logging(log_level)

    # Determine Iolanta instance based on node type
    if isinstance(node, Literal):
        # Literal nodes (e.g., from query results) are used directly
        # Use current directory as project_root for query results
        iolanta: Iolanta = Iolanta(
            language=Literal(language),
            logger=logger,
            project_root=Path.cwd(),
        )
    elif isinstance(node, URIRef):
        # URIRef - determine project_root if it's a file:// URI
        if str(node).startswith("file://"):
            path = Path(str(node).replace("file://", ""))
            iolanta: Iolanta = Iolanta(
                language=Literal(language),
                logger=logger,
                project_root=path,
            )
        else:
            iolanta: Iolanta = Iolanta(
                language=Literal(language),
                logger=logger,
            )
    else:
        # This should never happen due to type checking, but kept for safety
        raise TypeError(f"Expected Literal or URIRef, got {type(node)}")

    return iolanta.render(
        node=node,
        as_datatype=decode_datatype(as_datatype),
    )


@app.command(name="render")
def render_command(  # noqa: WPS231, WPS238, WPS210, C901
    url: Annotated[str | None, Argument()] = None,
    query: Annotated[
        str | None,
        Option(
            "--query",
            help="SPARQL query to execute.",
        ),
    ] = None,
    as_datatype: Annotated[
        str | None,
        Option(
            "--as",
        ),
    ] = None,
    language: Annotated[
        str,
        Option(
            help="Data language to prefer.",
        ),
    ] = DEFAULT_LANGUAGE,
    log_level: LogLevel = LogLevel.ERROR,
):
    """Render a given URL."""
    if query is not None:
        # For queries, default to 'table' format
        if as_datatype is None:
            as_datatype = "table"

        # Setup logging and create Iolanta instance (unlikely to raise)
        logger = setup_logging(log_level)
        iolanta: Iolanta = Iolanta(
            language=Literal(language),
            logger=logger,
            project_root=Path.cwd(),
        )

        try:
            renderable = render_and_return(
                node=create_query_node(iolanta.query(query)),
                as_datatype=as_datatype,
                language=language,
                log_level=log_level,
            )
        except (SPARQLParseException, DocumentedError, FacetNotFound) as error:
            handle_error(error, log_level, use_markdown=True)
        except Exception as error:
            handle_error(error, log_level, use_markdown=False)
        else:
            # FIXME: An intermediary Literal can be used to dispatch rendering.
            match renderable:
                case Table() as table:
                    console.print(table)

                case unknown:
                    console.print(unknown)
        return

    if url is None:
        console.print("Error: Either URL or --query must be provided")
        raise Exit(1)

    # For URLs, default to interactive mode
    if as_datatype is None:
        as_datatype = "https://iolanta.tech/cli/interactive"

    # Parse string URL to URIRef (URL() is permissive and won't raise)
    node_url = URL(url)
    if node_url.scheme and node_url.scheme != "file":
        node = URIRef(url)
    else:
        path = Path(node_url.path).absolute()
        node = URIRef(f"file://{path}")

    try:
        renderable = render_and_return(
            node=node,
            as_datatype=as_datatype,
            language=language,
            log_level=log_level,
        )
    except DocumentedError as error:
        handle_error(error, log_level, use_markdown=True)
    except Exception as error:
        handle_error(error, log_level, use_markdown=False)
    else:
        # FIXME: An intermediary Literal can be used to dispatch rendering.
        match renderable:
            case Table() as table:
                console.print(table)

            case unknown:
                console.print(unknown)
