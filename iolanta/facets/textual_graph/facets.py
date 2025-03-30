from textual.containers import VerticalScroll
from textual.widget import Widget

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.models import Triple
from iolanta.namespaces import DATATYPES


class GraphFacet(Facet[Widget]):
    """Display triples in a graph."""

    def show(self) -> Widget:
        """Show the widget."""
        triples = [
            Triple(triple['subject'], triple['predicate'], triple['object'])
            for triple in self.stored_query('triples.sparql', graph=self.iri)
        ]

        triple_count = len(triples)

        triples_view = self.iolanta.render(
            self.iri,
            as_datatype=DATATYPES['textual-graph-triples'],
        )

        return VerticalScroll(
            PageTitle(self.iri, extra=f'({triple_count} triples)'),
            triples_view,
        )
