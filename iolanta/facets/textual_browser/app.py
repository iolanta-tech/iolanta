from rdflib import URIRef
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Welcome, Button

from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


class Body(ScrollableContainer):
    """Browser body."""

    def on_mount(self):
        iolanta: Iolanta = self.app.iolanta
        iri: NotLiteralNode = self.app.iri
        self.mount(
            iolanta.render(
                iri,
                [URIRef('https://iolanta.tech/cli/textual')],
            )[0]
        )


class IolantaBrowser(App):
    """Browse Linked Data."""

    iolanta: Iolanta
    iri: NotLiteralNode

    BINDINGS = [
        ('g', 'goto', 'Go to URL'),
        ('s', 'search', 'Search'),
        ('t', 'toggle_dark', 'Toggle Dark Mode'),
        ('q', 'quit', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Body()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_goto(self, destination: str):
        body = self.query_one(Body)
        body.remove_children()

        self.iri = URIRef(destination)

        iolanta: Iolanta = self.iolanta
        iri: NotLiteralNode = self.iri
        body.mount(
            iolanta.render(
                iri,
                [URIRef('https://iolanta.tech/cli/textual')],
            )[0]
        )
