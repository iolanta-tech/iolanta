import funcy
from rdflib import URIRef
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

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

        return InstancesGrid([
            Label(str(instance))
            for instance in instances
        ])

        if instances:
            # Label('\n[bold]A few instances of this class[/]\n')
            children.append(Label(
                ' · '.join(
                    self.render(
                        instance,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    )
                    for instance in instances
                ),
            ))