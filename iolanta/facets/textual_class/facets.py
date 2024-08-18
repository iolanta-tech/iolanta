from functools import cached_property

import funcy
from rdflib import BNode, URIRef
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from iolanta.facets.facet import Facet
from iolanta.models import NotLiteralNode


class InstancesList(ListView):
    """Instances list."""

    instances = reactive[list[BNode | URIRef]](list, init=False)  # noqa: WPS462

    @cached_property
    def list_item_by_instance(self) -> dict[NotLiteralNode, ListItem]:
        """Generate a ListItem per class instance."""
        return {
            instance: ListItem(
                Label(
                    f'[red]…[/red] {instance}',
                ),
                disabled=True,
            )
            for instance in self.instances
        }

    def compose(self) -> ComposeResult:
        yield from self.list_item_by_instance.values()

    def render_instances(self):
        for instance, list_item in self.list_item_by_instance.items():
            list_item.query_one(Label).renderable = '⏳ Loading…'

            try:
                rendered = self.app.iolanta.render(
                    instance,
                    environments=[URIRef('https://iolanta.tech/cli/link')],
                )[0]
            except Exception as rendering_error:
                self.log(f'Failed to render {instance}: {rendering_error}')
                rendered = f'💥 {instance}'

            label = Label(rendered)

            self.app.call_from_thread(list_item.remove_children)
            self.app.call_from_thread(list_item.mount, label)
            list_item.disabled = False

    def on_mount(self):
        self.run_worker(self.render_instances, thread=True)


class Class(Facet[Widget]):
    def show(self) -> Widget:
        instances = funcy.lpluck(
            'instance',
            self.stored_query('instances.sparql', iri=self.iri),
        )

        instances_list = InstancesList()
        instances_list.instances = instances

        return instances_list
