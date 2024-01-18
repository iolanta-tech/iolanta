from textual.app import ReturnType

from iolanta.facets.facet import Facet, FacetOutput
from iolanta.facets.textual_browser.app import IolantaBrowser


class TextualBrowserFacet(Facet[ReturnType | None]):
    """Textual browser."""

    def show(self) -> ReturnType | None:
        app = IolantaBrowser()
        app.iolanta = self.iolanta
        app.iri = self.iri
        app.run()
