import functools
import uuid
from typing import cast

from rdflib import URIRef
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import (
    Footer, Header, Static,
    ContentSwitcher, Placeholder,
)
from textual.worker import Worker, WorkerState

from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


class Body(ContentSwitcher):
    """Browser body."""

    def on_mount(self):
        self.app.action_goto(self.app.iri)


class Home(Placeholder):
    def compose(self) -> ComposeResult:
        yield Static('Welcome to Iolanta! This is a placeholder page.')


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
        with Body(initial='home'):
            yield Home(id='home')
            # yield Body()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def render_iri(self, destination: str):
        self.iri = URIRef(destination)

        iolanta: Iolanta = self.iolanta
        iri: NotLiteralNode = self.iri
        return destination, self.call_from_thread(
            iolanta.render,
            iri,
            [URIRef('https://iolanta.tech/cli/textual')],
        )[0]

    def on_worker_state_changed(self, event: Worker.StateChanged):
        match event.state:
            case WorkerState.SUCCESS:
                iri, renderable = event.worker.result
                body = cast(Body, self.query_one(Body))
                page_id = f'page_{uuid.uuid4().hex}'
                body.mount(
                    ScrollableContainer(
                        renderable,
                        id=page_id,
                    )
                )
                body.current = page_id

            case WorkerState.ERROR:
                raise ValueError(event)

    def action_goto(self, destination: str):
        self.run_worker(
            functools.partial(
                self.render_iri,
                destination,
            ),
            thread=True,
        )
