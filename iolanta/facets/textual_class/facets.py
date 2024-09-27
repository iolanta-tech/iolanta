from functools import cached_property
from typing import ClassVar

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
        self.is_resolved = False
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

    def resolve(self):
        """Resolve the node for this item and render it."""
        if self.is_resolved:
            return

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
                self.is_resolved = True

            case WorkerState.ERROR:
                raise ValueError(event)


def indices_around(center: int, radius: int):
    """
    Generate indices around a center index within a given radius.

    Args:
        center (int): The center index around which to generate indices.
        radius (int): The maximum distance from the center.

    Yields:
        int: The next valid index around the center within the specified radius.
    """
    directions = [-1, 1]
    yield center
    for render_radius in range(1, radius + 1):
        for direction in directions:   # noqa: WPS526
            yield center + direction * render_radius


class InstancesList(ListView):   # noqa: WPS214
    """Instances list."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
        Binding('p', 'provenance', 'Provenan©e'),
    ]

    def __init__(
        self,
        instances: list[NotLiteralNode],
        parent_class: NotLiteralNode,
    ):
        """Specify the instances to render and their class."""
        self.instances = instances
        self.parent_class = parent_class
        super().__init__()

    @cached_property
    def list_item_by_instance(self) -> dict[NotLiteralNode, ListItem]:
        """Generate a ListItem per class instance."""
        return {
            instance: InstanceItem(
                node=instance,
                parent_class=self.parent_class,
            )
            for instance in self.instances
        }

    def compose(self) -> ComposeResult:
        yield from self.list_item_by_instance.values()

    def render_instances(self):
        """Render a number of instances around the one that is highlighted."""
        for index in indices_around(self.index or 0, INSTANCE_RENDER_RADIUS):
            if 0 <= index < len(self.instances):
                self._nodes[index].resolve()

    def on_mount(self):
        """Render a part of the list on creation."""
        self.run_worker(
            self.render_instances,
            group='render-list-items',
            thread=True,
            exclusive=True,
        )

    def on_list_view_selected(self):
        """Render a part of the list on selection."""
        self.run_worker(
            self.render_instances,
            group='render-list-items',
            thread=True,
            exclusive=True,
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


class Class(Facet[Widget]):
    """Render instances of a class."""

    def show(self) -> Widget:
        """Render the instances list."""
        instances = funcy.lpluck(
            'instance',
            self.stored_query('instances.sparql', iri=self.iri),
        )
        count = len(instances)

        return Vertical(
            InstancesList(
                instances=instances,
                parent_class=self.iri,
            ),
            Label(f'{count}+ instances'),
        )
