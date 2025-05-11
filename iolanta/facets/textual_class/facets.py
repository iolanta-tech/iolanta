import functools
import itertools
from typing import ClassVar, Iterable

import funcy
from rich.console import RenderResult
from rich.text import Text
from textual.binding import Binding, BindingType
from textual.containers import Vertical  # removed unused VerticalScroll (F401)
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.facets.textual_default.triple_uri_ref import TripleURIRef
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES, RDF

INSTANCE_RENDER_RADIUS = 50


class InstanceItem(ListItem):
    """An item in class instances list."""

    renderable: Reactive[RenderResult | None](None, init=True, layout=True)

    def __init__(
        self,
        node: NotLiteralNode,
        parent_class: NotLiteralNode,
    ):
        """Specify the node, its class, and that we are not rendered yet."""
        self.node = node
        self.parent_class = parent_class
        self.renderable = None
        super().__init__()

    def render(self) -> RenderResult:
        """
        Render this class instance.

        Render either the result or the raw node.

        # FIXME Calculate QName at least. Or CURIE? Or whatsit?
        """
        qname = self.app.iolanta.node_as_qname(self.node)
        return self.renderable or Text(
            f'⏳ {qname}',
            style='#696969',
        )

    def update(self, renderable: RenderResult):
        """
        Assign the render result.

        A separate method is needed for this because we call it from a thread.
        """
        self.renderable = renderable
        self.refresh()


class InstancesList(ListView):   # noqa: WPS214
    """Instances list."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
        Binding('p', 'provenance', 'Provenan©e'),
    ]

    DEFAULT_CSS = """
    InstancesList {
        height: 1fr;
        layout: vertical;
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

    def render_newly_added_instances(self, instance_items: list[InstanceItem]):
        """
        Render each of the given instance items.

        Must be called in a worker.
        """
        for instance_item in instance_items:
            self.app.call_from_thread(
                instance_item.update,
                self.app.iolanta.render(
                    instance_item.node,
                    as_datatype=DATATYPES.title,
                ),
            )

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

    def compose(self):
        """Fill in the instances."""
        for instance in self.instances:   # noqa: WPS526
            yield InstanceItem(
                node=instance,
                parent_class=self.parent_class,
            )

    def render_instances(self):
        """Render all instances."""
        for instance_item in self.children:
            self.app.call_from_thread(
                instance_item.update,
                self.app.iolanta.render(
                    instance_item.node,
                    as_datatype=DATATYPES.title,
                ),
            )

    def on_mount(self):
        """Render the first chunk of instances."""
        self.run_worker(
            self.render_instances,
            thread=True,
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
        return set(
            funcy.pluck(
                'instance',
                self.stored_query('instances.sparql', iri=self.iri),
            ),
        )

    def show(self) -> Widget:
        """Render the instances list."""
        return InstancesBody(
            PageTitle(self.iri),
            InstancesList(
                instances=list(self.stream_instances()),
                parent_class=self.iri,
            ),
        )
