import functools

from rdflib import URIRef
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Footer, Header, Welcome

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
            )[0],
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

    def goto(self, destination: str):
        self.iri = URIRef(destination)

        iolanta: Iolanta = self.iolanta
        iri: NotLiteralNode = self.iri
        return self.call_from_thread(
            iolanta.render,
            iri,
            [URIRef('https://iolanta.tech/cli/textual')],
        )[0]

    def action_goto(self, destination: str):
        body = self.query_one(Body)
        rendered = self.run_worker(
            functools.partial(
                self.goto,
                destination,
            ),
            thread=True,
        )
        body.remove_children()
        body.mount(rendered)
