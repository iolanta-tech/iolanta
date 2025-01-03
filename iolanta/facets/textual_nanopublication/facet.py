from textual.widget import Widget

from iolanta import Facet
from iolanta.facets.textual_nanopublication.nanopublication_widget import (
    NanopublicationScreen,
)


class NanopublicationFacet(Facet[Widget]):
    """Render a nanopublication."""

    def show(self) -> Widget:
        """Render a nanopublication."""
        return NanopublicationScreen(uri=self.iri)
