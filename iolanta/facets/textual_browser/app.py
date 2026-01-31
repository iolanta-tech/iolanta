import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast

from rdflib.term import Node
from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Footer, Header

from iolanta.facets.textual_browser.page_switcher import (
    ConsoleSwitcher,
    DevConsole,
    PageSwitcher,
)
from iolanta.iolanta import Iolanta

POPUP_TIMEOUT = 30  # seconds


class DevConsoleHandler(logging.Handler):
    """Pipe log output → dev console."""

    def __init__(self, console: DevConsole, level=logging.NOTSET) -> None:
        """Set parameters."""
        self.console = console
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord) -> None:
        """Write a message when invoked by `logging`."""
        message = self.format(record)
        self.console.write(message)


def _log_message_to_dev_console(app: App[None]):
    """Log a message to the dev console."""

    def log_message_to_dev_console(message: str):  # noqa: WPS430
        try:
            app.query_one(DevConsole).write(message)
        except NoMatches:
            return

    return log_message_to_dev_console


class IolantaBrowser(App[None]):  # noqa: WPS214, WPS230
    """Browse Linked Data."""

    def __init__(self, iolanta: Iolanta, this: Node):
        """Set up parameters for the browser."""
        self.iolanta = iolanta
        self.this = this
        self.renderers = ThreadPoolExecutor()
        super().__init__()

    BINDINGS = [  # noqa: WPS115
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose widgets."""
        yield Header(icon="👁️")
        yield Footer()
        yield ConsoleSwitcher()  # type: ignore[no-untyped-call]

    def on_mount(self):
        """Set title."""
        self.title = "Iolanta"

        logging.basicConfig(
            level=logging.INFO,
            handlers=[
                DevConsoleHandler(
                    console=self.query_one(DevConsole),
                    level=logging.INFO,
                ),
            ],
            force=True,
        )

        # Disable stderr logging, to not break the TUI.
        # Remove only the stderr handler, keep file handler (loguru API)
        loguru_logger = cast(Any, self.iolanta.logger)
        logger_core = loguru_logger._core
        for handler_id in list(logger_core.handlers.keys()):
            log_handler = logger_core.handlers[handler_id]
            if hasattr(log_handler, "sink") and str(log_handler.sink) == "<stderr>":
                loguru_logger.remove(handler_id)

        # Log to the dev console.
        loguru_logger.add(
            _log_message_to_dev_console(self),
            level="INFO",
            format="{time} {level} {message}",
        )

        loguru_logger.add(
            lambda msg: self.notify(
                msg,
                severity="warning",
                timeout=POPUP_TIMEOUT,
            ),
            level="WARNING",
            format="{message}",
        )

    def action_goto(
        self,
        destination: Node | str,
        facet_iri: str | None = None,
    ) -> None:
        """Go to an IRI."""
        self.query_one(PageSwitcher).action_goto(destination, facet_iri)

    def dev_console_log(self, renderable: RenderableType | object):
        """Print a renderable to the dev console."""
        self.query_one(DevConsole).write(renderable)
