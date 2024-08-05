import functools
import uuid
from dataclasses import dataclass
from typing import cast

import funcy
from rdflib import URIRef
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, Footer, Header, Placeholder, Static
from textual.widgets._header import HeaderTitle
from textual.worker import Worker, WorkerState

from iolanta.facets.textual_browser.history import NavigationHistory
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


@dataclass
class Location:
    page_id: str
    url: str


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

    @functools.cached_property
    def history(self) -> NavigationHistory[Location]:
        return NavigationHistory[Location]()

    BINDINGS = [
        ('alt+left', 'back', 'Back'),
        ('alt+right', 'forward', 'Fwd'),
        # ('g', 'goto', 'Go to URL'),
        # ('s', 'search', 'Search'),
        ('t', 'toggle_dark', 'Toggle Dark Mode'),
        ('q', 'quit', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon='👁️')
        yield Footer()
        with Body(initial='home'):
            yield Home(id='home')

    def on_mount(self):
        self.title = 'Iolanta'

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
                    ),
                )
                body.current = page_id
                self.history.goto(Location(page_id, iri))

                title = cast(HeaderTitle, self.query_one(HeaderTitle))
                title.sub_text = iri

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

    def action_back(self):
        self.query_one(Body).current = self.history.back().page_id

    def action_forward(self):
        self.query_one(Body).current = self.history.forward().page_id
