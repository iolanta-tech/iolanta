import functools
import uuid
from dataclasses import dataclass
from typing import cast

from rdflib import BNode, URIRef
from textual import events
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.events import Key, MouseEvent
from textual.widgets import ContentSwitcher, Footer, Header, Placeholder, Static
from textual.worker import Worker, WorkerState

from iolanta.facets.textual_browser.history import NavigationHistory
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


@dataclass
class Location:
    """Unique ID and IRI associated with it."""

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
    alt_click: bool = False

    @functools.cached_property
    def history(self) -> NavigationHistory[Location]:
        """Cached navigation history."""
        return NavigationHistory[Location]()

    BINDINGS = [  # noqa: WPS115
        ('alt+left', 'back', 'Back'),
        ('alt+right', 'forward', 'Fwd'),
        ('t', 'toggle_dark', 'Toggle Dark Mode'),
        ('q', 'quit', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        """Compose widgets."""
        yield Header(icon='👁️')
        yield Footer()
        with Body(initial='home'):
            yield Home(id='home')

    def on_mount(self):
        """Set title."""
        self.title = 'Iolanta'

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def render_iri(self, destination: NotLiteralNode):
        """Render an IRI in a thread."""
        self.iri = destination

        iolanta: Iolanta = self.iolanta
        iri: NotLiteralNode = self.iri
        return destination, self.call_from_thread(
            iolanta.render,
            iri,
            [URIRef('https://iolanta.tech/cli/textual')],
        )[0]

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Render a page as soon as it is ready."""
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
                self.sub_title = iri

            case WorkerState.ERROR:
                raise ValueError(event)

    def on_mouse_down(self, event: MouseEvent):
        self.alt_click = event.meta

    def on_mouse_up(self, event: MouseEvent):
        self.alt_click = False

    def action_goto(
        self,
        destination: str,
        iri_type_name: str | None = None,
    ):
        """Go to an IRI."""
        iri_type = {
            None: URIRef,
            'BNode': BNode,
            'URIRef': URIRef,
        }[iri_type_name]

        iri = iri_type(destination)

        self.run_worker(
            functools.partial(
                self.render_iri,
                iri,
            ),
            thread=True,
        )

    def action_back(self):
        """Go backward."""
        self.query_one(Body).current = self.history.back().page_id

    def action_forward(self):
        """Go forward."""
        self.query_one(Body).current = self.history.forward().page_id
