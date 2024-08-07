import logging

from textual.app import ReturnType
from textual.logging import TextualHandler

from iolanta.facets.facet import Facet, FacetOutput
from iolanta.facets.textual_browser.app import IolantaBrowser

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class TextualBrowserFacet(Facet[ReturnType | None]):
    """Textual browser."""

    def show(self) -> ReturnType | None:
        app = IolantaBrowser()
        app.iolanta = self.iolanta
        app.iri = self.iri
        try:
            app.run()
        except Exception:
            logging.exception("Unhandled exception.")
