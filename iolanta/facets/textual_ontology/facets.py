import funcy
from rdflib import URIRef
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static

from iolanta.facets.facet import Facet


class OntologyTerms(DataTable):
    def on_data_table_cell_selected(self, event: DataTable.CellHighlighted):
        raise ValueError(event.value)


class OntologyFacet(Facet[Widget]):
    def show(self) -> Widget:
        terms = funcy.lpluck(
            'term',
            self.stored_query('terms.sparql', iri=self.iri),
        )

        renderables = [
            self.render(
                term,
                environments=[URIRef('https://iolanta.tech/env/title')],
            )
            for term in terms
        ]

        rows = funcy.chunks(3, renderables)

        table = OntologyTerms(show_header=False)
        table.add_columns('1', '2', '3')

        table.add_rows(rows)

        return table
