import funcy
from rdflib import URIRef
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, Button, Static, ListView, ListItem

from iolanta.facets.facet import Facet


class InstancesGrid(Vertical):
    DEFAULT_CSS = """
    InstancesGrid {
        layout: grid;
        grid-size: 3 2;
    }
    """


class Class(Facet[Widget]):
    def show(self) -> Widget:
        instances = funcy.lpluck(
            'instance',
            self.stored_query('instances.sparql', iri=self.iri),
        )

        return ListView(*[
            ListItem(
                Label(
                    self.render(
                        instance,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    ),
                )
            )
            for instance in instances
        ])
