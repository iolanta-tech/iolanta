import logging

from textual.app import ReturnType
from textual.logging import TextualHandler

from iolanta.facets.facet import Facet, FacetOutput
from iolanta.facets.textual_browser.app import IolantaBrowser


class TextualBrowserFacet(Facet[ReturnType | None]):
    """Textual browser."""

    def show(self) -> ReturnType | None:
        """Render the Iolanta browser Textual app."""
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[TextualHandler()],
            force=True,
        )

        app = IolantaBrowser(
            iolanta=self.iolanta,
            iri=self.iri,
        )
        try:
            app.run()
        except Exception:
            logging.exception("Unhandled exception.")
