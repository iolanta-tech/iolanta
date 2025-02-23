import functools
import threading
import uuid
from dataclasses import dataclass
from typing import Annotated, Any

import watchfiles
from rdflib import BNode, URIRef
from textual.widgets import ContentSwitcher, RichLog
from textual.worker import Worker, WorkerState

from iolanta.facets.errors import FacetError, FacetNotFound
from iolanta.facets.locator import FacetFinder
from iolanta.facets.textual_browser.history import NavigationHistory
from iolanta.facets.textual_browser.home import Home
from iolanta.facets.textual_browser.location import Location
from iolanta.facets.textual_browser.models import FlipOption
from iolanta.facets.textual_browser.page import Page
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin


@dataclass
class RenderResult:
    """
    We asked a thread to render something for us.

    This is what did we get back.
    """

    iri: NotLiteralNode
    renderable: Any
    flip_options: list[FlipOption]
    facet_iri: URIRef
    is_reload: bool


class PageSwitcher(IolantaWidgetMixin, ContentSwitcher):  # noqa: WPS214
    """
    Container for open pages.

    Able to navigate among them while traversing the history.
    """

    BINDINGS = [  # noqa: WPS115
        ('alt+left', 'back', 'Back'),
        ('alt+right', 'forward', 'Fwd'),
        ('f5', 'reload', 'Reload'),
        ('escape', 'abort', 'Abort'),
        ('f12', 'console', 'Console'),
    ]

    def __init__(self):
        """Set Home as first tab."""
        super().__init__(id='page_switcher', initial='home')
        self.stop_file_watcher_event = threading.Event()
        self.loader_worker: Annotated[
            Worker | None,
            'Worker presently loading & rendering a page.',
        ] = None

    def action_console(self):
        """Open dev console."""
        console_switcher = self.app.query_one(ConsoleSwitcher)
        console_switcher.current = 'console'
        console_switcher.query_one(DevConsole).focus()

    @functools.cached_property
    def history(self) -> NavigationHistory[Location]:
        """Cached navigation history."""
        return NavigationHistory[Location]()

    def compose(self):
        """Home is the first page to open."""
        yield Home(id='home')

    def on_mount(self):
        """Navigate to the initial page."""
        self.action_goto(self.app.iri)
        if self.iolanta.project_root:
            self.run_worker(
                self._watch_files,
                thread=True,
            )

    def on_unmount(self) -> None:
        """Stop watching files."""
        self.stop_file_watcher_event.set()

    def _watch_files(self):
        for _ in watchfiles.watch(   # noqa: WPS352
            self.iolanta.project_root,
            stop_event=self.stop_file_watcher_event,
        ):
            self.app.call_from_thread(self.action_reload)

    def render_iri(   # noqa: WPS210
        self,
        destination: NotLiteralNode,
        facet_iri: URIRef | None,
        is_reload: bool,
    ) -> RenderResult:
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
            for choice in choices
            if choice['facet'] != facet_iri
        ]
        flip_options = [
            FlipOption(
                facet_iri=facet,
                title=self.app.call_from_thread(
                    self.iolanta.render,
                    facet,
                    as_datatype=DATATYPES.title,
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
            renderable = self.app.call_from_thread(facet.show)

        except Exception as err:
            raise FacetError(
                node=self.iri,
                facet_iri=facet_iri,
                error=err,
            ) from err

        return RenderResult(
            iri=destination,
            renderable=renderable,
            flip_options=flip_options,
            facet_iri=facet_iri,
            is_reload=is_reload,
        )

    def on_worker_state_changed(   # noqa: WPS210
        self,
        event: Worker.StateChanged,
    ):
        """Render a page as soon as it is ready."""
        self.loader_worker = None

        match event.state:
            case WorkerState.SUCCESS:
                render_result: RenderResult = event.worker.result

                if render_result.is_reload:
                    # We are reloading the current page.
                    current_page = self.query_one(f'#{self.current}', Page)
                    current_page.remove_children()
                    current_page.mount(render_result.renderable)

                    # FIXME: This does not actually change the flip options,
                    #   but maybe that's okay
                    current_page.flip_options = render_result.flip_options

                else:
                    # We are navigating to a new page.
                    page_uid = uuid.uuid4().hex
                    page_id = f'page_{page_uid}'
                    page = Page(
                        render_result.renderable,
                        iri=render_result.iri,
                        page_id=page_id,
                        flip_options=render_result.flip_options,
                    )
                    self.mount(page)
                    self.current = page_id
                    page.focus()
                    self.history.goto(
                        Location(
                            page_id,
                            url=render_result.iri,
                            facet_iri=render_result.facet_iri,
                        ),
                    )
                    self.app.sub_title = render_result.iri

            case WorkerState.ERROR:
                raise ValueError(event)

    def action_reload(self):
        """Reset Iolanta graph and re-render current view."""
        self.iolanta.reset()

        self.loader_worker = self.run_worker(
            functools.partial(
                self.render_iri,
                destination=self.history.current.url,
                facet_iri=self.history.current.facet_iri,
                is_reload=True,
            ),
            thread=True,
        )
        self.refresh_bindings()

    def action_abort(self):
        """Abort loading."""
        self.notify(
            'Aborted',
            severity='warning',
        )
        self.loader_worker.cancel()
        self.loader_worker = None
        self.refresh_bindings()

    def check_action(
        self,
        action: str,
        parameters: tuple[object, ...],   # noqa: WPS110
    ) -> bool | None:
        """Check if action is available."""
        is_loading = self.loader_worker is not None
        if is_loading:
            raise ValueError(action, parameters, 'is loading')
        match action:
            case 'reload':
                return not is_loading
            case 'abort':
                return is_loading

        return True

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

        self.loader_worker = self.run_worker(
            functools.partial(
                self.render_iri,
                destination=iri,
                facet_iri=facet_iri and URIRef(facet_iri),
                is_reload=False,
            ),
            thread=True,
        )
        self.refresh_bindings()

    def action_back(self):
        """Go backward."""
        self.current = self.history.back().page_id
        self.focus()

    def action_forward(self):
        """Go forward."""
        self.current = self.history.forward().page_id
        self.focus()


class ConsoleSwitcher(ContentSwitcher):
    """Switch between page switcher and dev console."""

    def __init__(self):
        """Specify initial params."""
        super().__init__(
            id='console_switcher',
            initial='page_switcher',
        )

    def compose(self):
        """Compose two tabs."""
        yield PageSwitcher()
        yield DevConsole()


class DevConsole(RichLog):
    """Development console."""

    BINDINGS = [
        ('f12,escape', 'close', 'Close Console'),
    ]

    def __init__(self):
        """Set default props for console."""
        super().__init__(highlight=True, markup=True, id='console')

    def action_close(self):
        """Close the dev console."""
        console_switcher = self.app.query_one(ConsoleSwitcher)
        console_switcher.current = 'page_switcher'

        page_switcher = console_switcher.query_one(PageSwitcher)
        page_switcher.visible_content.focus()
