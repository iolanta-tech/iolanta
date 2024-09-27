import functools
from functools import cached_property
from typing import ClassVar

import funcy
from rdflib import RDF, URIRef
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.scrollbar import ScrollDown
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from iolanta.facets.facet import Facet
from iolanta.facets.textual_default.facets import TripleURIRef
from iolanta.models import NotLiteralNode


class InstanceItem(ListItem):
    def __init__(self, node: NotLiteralNode, parent_class: NotLiteralNode):
        self.node = node
        self.parent_class = parent_class
        self.is_resolved = False
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(str(self.node))

    def render_content(self):
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
        max_render_radius = 10
        if self.index:
            self.highlighted_child.resolve()
            highlighted_index = self.index
        else:
            highlighted_index = 0

        for render_radius in range(1, max_render_radius + 1):
            for direction in [-1, 1]:
                index = highlighted_index + direction * render_radius

                if index < 0:
                    continue

                if index >= len(self.instances):
                    continue

                self._nodes[index].resolve()

    def on_mount(self):
        self.run_worker(self.render_instances, thread=True, exclusive=True)

    def on_list_view_selected(self):
        self.run_worker(self.render_instances, thread=True, exclusive=True)

    def on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
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
