from textual.widget import Widget
from textual.widgets import Label

from iolanta.facets.facet import Facet, FacetOutput


class OntologyFacet(Facet[Widget]):
    def show(self) -> Widget:
        return Label('I AM AN ONTOLOGY')
