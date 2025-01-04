import logging
from concurrent.futures import ThreadPoolExecutor

from rdflib.term import Node
from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from iolanta.facets.textual_browser.page_switcher import (
    ConsoleSwitcher,
    DevConsole,
    PageSwitcher,
)
from iolanta.iolanta import Iolanta


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


class IolantaBrowser(App):  # noqa: WPS214, WPS230
    """Browse Linked Data."""

    def __init__(self, iolanta: Iolanta, iri: Node):
        """Set up parameters for the browser."""
        self.iolanta = iolanta
        self.iri = iri
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
        self.iolanta.logger.remove(0)

        # Log to the dev console.
        self.iolanta.logger.add(
            lambda msg: self.query_one(DevConsole).write(msg),
            level='INFO',
            format='{time} {level} {message}',
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
