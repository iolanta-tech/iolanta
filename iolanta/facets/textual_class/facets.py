from functools import cached_property
from typing import ClassVar

import funcy
from rdflib import RDF, URIRef
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from iolanta.facets.facet import Facet
from iolanta.facets.textual_default.facets import TripleURIRef
from iolanta.models import NotLiteralNode


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
        yield Label(str(self.node))

    def render_content(self):
        """Replace plain URI with a rendered human readable title."""
        renderable = self.app.iolanta.render(
            self.node,
            environments=[URIRef('https://iolanta.tech/env/title')],
        )[0]
        self.app.call_from_thread(
            self.query_one(Label).update,
            renderable,
        )
        self.is_resolved = True

    def resolve(self):
        """Resolve the node for this item and render it."""
        if self.is_resolved:
            return

        self.run_worker(self.render_content, thread=True, exclusive=True)


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
        for direction in directions:
            yield center + direction * render_radius


class InstancesList(ListView):
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
        for index in indices_around(self.index or 0, 10):
            if 0 < index <= len(self.instances):
                self._nodes[index].resolve()

    def on_mount(self):
        self.run_worker(self.render_instances, thread=True, exclusive=True)

    def on_list_view_selected(self):
        self.run_worker(self.render_instances, thread=True, exclusive=True)

    def on_list_item__child_clicked(self) -> None:
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
        instances = funcy.lpluck(
            'instance',
            self.stored_query('instances.sparql', iri=self.iri),
        )
        count = len(instances)

        return Vertical(
            Label(f'{count}+ instances'),
            InstancesList(
                instances=instances,
                parent_class=self.iri,
            ),
        )
