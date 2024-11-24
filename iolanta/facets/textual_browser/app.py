from concurrent.futures import ThreadPoolExecutor

from rdflib.term import Node
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from iolanta.facets.textual_browser.page_switcher import (
    ConsoleSwitcher,
    PageSwitcher,
)
from iolanta.iolanta import Iolanta


class IolantaBrowser(App):   # noqa: WPS214, WPS230
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
