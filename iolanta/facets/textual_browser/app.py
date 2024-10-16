import functools
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import cast

from rdflib import BNode, URIRef
from rdflib.term import Node
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import ContentSwitcher, Footer, Header, Placeholder, Static
from textual.worker import Worker, WorkerState

from iolanta.facets.errors import FacetError, FacetNotFound
from iolanta.facets.locator import FacetFinder
from iolanta.facets.textual_browser.history import NavigationHistory
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


@dataclass
class FlipOption:
    """Option to flip to another facet."""

    facet_iri: URIRef
    title: str


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
        iri: NotLiteralNode,
        page_id: str,
        flip_options: list[FlipOption],
    ):
        """Initialize the page and set bindings."""
        super().__init__(renderable, id=page_id)
        for number, flip_option in enumerate(flip_options, start=1):
            self._bindings.bind(
                keys={
                    1: 'ctrl+j',
                    2: 'ctrl+k',
                    3: 'ctrl+l',
                    4: 'ctrl+;',
                }[number],
                description=flip_option.title,
                action=(
                    f"app.goto('{iri}', '{flip_option.facet_iri}')"
                ),
            )


class IolantaBrowser(App):   # noqa: WPS214, WPS230
    """Browse Linked Data."""

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

    def render_iri(   # noqa: WPS210
        self, destination: NotLiteralNode, facet_iri: URIRef | None,
    ):
        """Render an IRI in a thread."""
        self.iri = destination
        iolanta: Iolanta = self.iolanta

        as_datatype = URIRef('https://iolanta.tech/cli/textual')
        choices = self.app.call_from_thread(
            FacetFinder(
                iolanta=self.iolanta,
                node=destination,
                as_datatype=as_datatype,
            ).choices,
        )

        if not choices:
            raise FacetNotFound(
                node=self.iri,
                as_datatype=as_datatype,
                node_types=[],
            )

        if facet_iri is None:
            facet_iri = choices[0]['facet']

        other_facets = [
            choice['facet']
            for choice
            in choices
            if choice['facet'] != facet_iri
        ]
        flip_options = [
            FlipOption(
                facet_iri=facet,
                title=self.app.call_from_thread(
                    self.iolanta.render,
                    facet,
                    as_datatype=URIRef('https://iolanta.tech/env/title'),
                )[0],
            )
            for facet in other_facets
        ]

        facet_class = iolanta.facet_resolver[facet_iri]

        facet = facet_class(
            iri=self.iri,
            iolanta=iolanta,
            as_datatype=URIRef('https://iolanta.tech/cli/textual'),
        )

        try:
            return (
                destination,
                self.app.call_from_thread(facet.show),
                flip_options,
            )

        except Exception as err:
            raise FacetError(
                node=self.iri,
                facet_iri=facet_iri,
                error=err,
            ) from err

    def on_worker_state_changed(   # noqa: WPS210
        self,
        event: Worker.StateChanged,
    ):
        """Render a page as soon as it is ready."""
        match event.state:
            case WorkerState.SUCCESS:
                iri, renderable, flip_options = event.worker.result
                body = cast(Body, self.query_one(Body))
                page_uid = uuid.uuid4().hex
                page_id = f'page_{page_uid}'
                page = Page(
                    renderable,
                    iri=iri,
                    page_id=page_id,
                    flip_options=flip_options,
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
        facet_iri: str | None = None,
    ):
        """Go to an IRI."""
        if destination.startswith('_:'):
            iri = BNode(destination)
        else:
            iri = URIRef(destination)

        self.run_worker(
            functools.partial(
                self.render_iri,
                iri,
                facet_iri and URIRef(facet_iri),
            ),
            thread=True,
        )

    def action_back(self):
        """Go backward."""
        self.query_one(Body).current = self.history.back().page_id

    def action_forward(self):
        """Go forward."""
        self.query_one(Body).current = self.history.forward().page_id
