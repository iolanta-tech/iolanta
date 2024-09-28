import itertools
from typing import ClassVar, Iterable

import funcy
from rdflib import RDF, URIRef
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView
from textual.worker import Worker, WorkerState

from iolanta.facets.facet import Facet
from iolanta.facets.textual_default.facets import TripleURIRef
from iolanta.models import NotLiteralNode

INSTANCE_RENDER_RADIUS = 50


class InstanceLabel(Label):
    """Instance URI or rendered title."""

    DEFAULT_CSS = """
    InstanceLabel {
        color: gray;
    }
    """


class InstanceItem(ListItem):
    """An item in class instances list."""

    def __init__(self, node: NotLiteralNode, parent_class: NotLiteralNode):
        """Specify the node, its class, and that we are not rendered yet."""
        self.node = node
        self.parent_class = parent_class
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        By default, we render plain URI of the class instance.

        # FIXME Calculate QName maybe?
        """
        yield InstanceLabel(str(self.node))

    def render_content(self):
        """Replace plain URI with a rendered human readable title."""
        return self.app.iolanta.render(
            self.node,
            environments=[URIRef('https://iolanta.tech/env/title')],
        )[0]

    def on_mount(self):
        """Resolve the node for this item and render it."""
        self.run_worker(
            self.render_content,
            group='render-list-item',
            thread=True,
            exclusive=True,
        )

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Show the title after it has been rendered."""
        match event.state:
            case WorkerState.SUCCESS:
                label = self.query_one(InstanceLabel)
                label.renderable = event.worker.result   # noqa: WPS601
                label.styles.color = 'white'

            case WorkerState.ERROR:
                raise ValueError(event)


class InstancesList(ListView):   # noqa: WPS214
    """Instances list."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
        Binding('p', 'provenance', 'Provenan©e'),
    ]

    DEFAULT_CSS = """
    InstancesList {
        height: auto;
        
        layout: vertical;
        overflow-x: hidden;
        overflow-y: auto;
    }
    """

    FIRST_CHUNK_SIZE = 15
    DEFAULT_CHUNK_SIZE = 10

    def __init__(
        self,
        instances: Iterable[NotLiteralNode],
        parent_class: NotLiteralNode,
    ):
        """Specify the instances to render and their class."""
        self.instances = instances
        self.parent_class = parent_class
        super().__init__()

    def compose(self) -> ComposeResult:
        """Load the first chunk of items."""
        yield from self.stream_instance_items_chunk(count=self.FIRST_CHUNK_SIZE)

    def stream_instance_items_chunk(
        self,
        count: int | None = None,
    ) -> Iterable[InstanceItem]:
        """Return a chunk of unique class instances."""
        chunk = itertools.islice(
            self.instances,
            count or self.DEFAULT_CHUNK_SIZE,
        )
        for instance in chunk:  # noqa: WPS526
            yield InstanceItem(
                node=instance,
                parent_class=self.parent_class,
            )

    def on_list_view_highlighted(self):
        """
        Find out whether the last item of the list is highlighted.

        If yes then add more elements.
        """
        if not self._nodes:
            return

        if self.index >= len(self._nodes) - 1:
            self.extend(
                self.stream_instance_items_chunk(),
            )

    def on_list_item__child_clicked(self) -> None:   # noqa: WPS116
        """Navigate on click."""
        # FIXME if we call `action_goto()` here we'll navigate to the item that
        #   was selected _prior_ to this click.

    def action_goto(self):
        """Navigate."""
        self.app.action_goto(self.highlighted_child.node)

    def action_provenance(self):
        """Navigate to provenance for the property value."""
        self.app.action_goto(
            TripleURIRef.from_triple(
                subject=self.highlighted_child.node,
                predicate=RDF.type,
                object_=self.parent_class,
            ),
        )


class Bottom(Label):
    """Label below the instances list."""

    DEFAULT_CSS = """
    Bottom {
        padding-top: 1;
        padding-bottom: 1;
        dock: bottom;
    }
    """


class InstancesBody(Vertical):
    """Container for instances list and accompanying bells and whistles."""

    DEFAULT_CSS = """
    InstancesBody {
        height: auto;
        max-height: 100%;
    }
    """


class Class(Facet[Widget]):
    """Render instances of a class."""

    def stream_instances(self) -> Iterable[NotLiteralNode]:
        """
        Query and stream class instances lazily.

        The operation of rendering an instance is not pure: it might cause us
        to retrieve more data and load said data into the graph. That's because
        we do multiple query attempts.

        We have to stop if a subsequent attempt returns no results. That's why
        we can't use `funcy.distinct()` or something similar.
        """
        known_instances: set[NotLiteralNode] = set()
        while True:
            instances = set(
                funcy.pluck(
                    'instance',
                    self.stored_query('instances.sparql', iri=self.iri),
                ),
            ).difference(known_instances)

            if not instances:
                return

            yield from instances

            known_instances.update(instances)

    def show(self) -> Widget:
        """Render the instances list."""
        return InstancesBody(
            InstancesList(
                instances=self.stream_instances(),
                parent_class=self.iri,
            ),
            Bottom('Select the last element to try loading more instances.'),
        )
