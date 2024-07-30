import functools

from rdflib import URIRef
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Footer, Header, Welcome, Label, Static
from textual.worker import Worker, WorkerState

from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


class Body(ScrollableContainer):
    """Browser body."""

    def on_mount(self):
        self.app.action_goto(self.app.iri)


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
        yield Footer(Static('status'))
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

    def on_worker_state_changed(self, event: Worker.StateChanged):
        match event.state:
            case WorkerState.SUCCESS:
                renderable = event.worker.result
                body = self.query_one(Body)
                body.remove_children()
                body.mount(renderable)

            case WorkerState.ERROR:
                raise ValueError(event)

    def action_goto(self, destination: str):
        self.run_worker(
            functools.partial(
                self.goto,
                destination,
            ),
            thread=True,
        )
