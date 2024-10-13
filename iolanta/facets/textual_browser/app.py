import functools
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import cast

from rdflib import BNode, URIRef
from rdflib.term import Node
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import ContentSwitcher, Footer, Header, Placeholder, Static
from textual.worker import Worker, WorkerState

from iolanta.facets.errors import FacetError, FacetNotFound
from iolanta.facets.locator import FacetFinder
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


class Page(ScrollableContainer):
    """Page in Iolanta browser."""

    def __init__(
        self,
        renderable,
        page_id: str,
        bindings: list[Binding] | None = None,
    ):
        """Initialize the page and set bindings."""
        super().__init__(renderable, id=page_id)
        if bindings:
            for binding in bindings:
                self._bindings.keys[binding.key] = binding


class IolantaBrowser(App):   # noqa: WPS214, WPS230
    """Browse Linked Data."""

    alt_click: bool = False

    def __init__(self, iolanta: Iolanta, iri: Node):
        """Set up parameters for the browser."""
        self.iolanta = iolanta
        self.iri = iri
        self.renderers = ThreadPoolExecutor()
        super().__init__()

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

    def render_iri(self, destination: NotLiteralNode):  # noqa: WPS210
        """Render an IRI in a thread."""
        self.iri = destination
        iolanta: Iolanta = self.iolanta

        environments = [URIRef('https://iolanta.tech/cli/textual')]
        choices = self.app.call_from_thread(
            FacetFinder(
                iolanta=self.iolanta,
                node=destination,
                environments=environments,
            ).choices,
        )

        if not choices:
            raise FacetNotFound(
                node=self.iri,
                environments=environments,
                node_types=[],
            )

        found = choices[0]

        if len(choices) > 1:
            raise ValueError(f'TODO: display choices {choices}')

        facet_class = iolanta.facet_resolver[found['facet']]

        facet = facet_class(
            iri=self.iri,
            iolanta=iolanta,
            environment=found['environment'],
        )

        try:
            return destination, self.app.call_from_thread(facet.show)

        except Exception as err:
            raise FacetError(
                node=self.iri,
                facet_iri=found['facet'],
                error=err,
            ) from err

    def on_worker_state_changed(   # noqa: WPS210
        self,
        event: Worker.StateChanged,
    ):
        """Render a page as soon as it is ready."""
        match event.state:
            case WorkerState.SUCCESS:
                iri, renderable = event.worker.result
                body = cast(Body, self.query_one(Body))
                page_uid = uuid.uuid4().hex
                page_id = f'page_{page_uid}'
                page = Page(
                    renderable,
                    page_id=page_id,
                    bindings=[
                        # Binding(
                        #     key='ctrl+j',
                        #     action='goto_json()',
                        #     description='JSON',
                        # ),
                    ],
                )
                body.mount(page)
                body.current = page_id
                page.focus()
                self.history.goto(Location(page_id, iri))
                self.sub_title = iri

            case WorkerState.ERROR:
                raise ValueError(event)

    def action_goto(
        self,
        destination: str,
        iri_type_name: str | None = None,
    ):
        """
        Go to an IRI.

        TODO: Remove iri_type_name, recognize a blank node based on destination.
        """
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
