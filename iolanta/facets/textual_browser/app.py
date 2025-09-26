import logging
from concurrent.futures import ThreadPoolExecutor

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

POPUP_TIMEOUT = 30   # seconds


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


def _log_message_to_dev_console(app: App):
    """Log a message to the dev console."""
    def log_message_to_dev_console(message: str):   # noqa: WPS430
        try:
            app.query_one(DevConsole).write(message)
        except NoMatches:
            return

    return log_message_to_dev_console


class IolantaBrowser(App):  # noqa: WPS214, WPS230
    """Browse Linked Data."""

    def __init__(self, iolanta: Iolanta, this: Node):
        """Set up parameters for the browser."""
        self.iolanta = iolanta
        self.this = this
        self.renderers = ThreadPoolExecutor()
        super().__init__()

    BINDINGS = [  # noqa: WPS115
        ('t', 'toggle_dark', 'Toggle Dark Mode'),
        ('q', 'quit', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        """Compose widgets."""
        yield Header(icon='👁️')
        yield Footer()
        yield ConsoleSwitcher()

    def on_mount(self):
        """Set title."""
        self.title = 'Iolanta'

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
        # Remove only the stderr handler, keep file handler
        for handler_id in list(self.iolanta.logger._core.handlers.keys()):
            handler = self.iolanta.logger._core.handlers[handler_id]
            if hasattr(handler, 'sink') and str(handler.sink) == '<stderr>':
                self.iolanta.logger.remove(handler_id)

        # Log to the dev console.
        self.iolanta.logger.add(
            _log_message_to_dev_console(self),
            level='INFO',
            format='{time} {level} {message}',
        )

        self.iolanta.logger.add(
            lambda msg: self.notify(
                msg,
                severity='warning',
                timeout=POPUP_TIMEOUT,
            ),
            level='WARNING',
            format='{message}',
        )

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_goto(
        self,
        destination: str,
        facet_iri: str | None = None,
    ):
        """Go to an IRI."""
        self.query_one(PageSwitcher).action_goto(destination, facet_iri)

    def dev_console_log(self, renderable: RenderableType | object):
        """Print a renderable to the dev console."""
        self.query_one(DevConsole).write(renderable)
