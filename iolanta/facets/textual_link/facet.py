from rdflib import Literal, URIRef
from rich.style import Style
from rich.text import Text

from iolanta.facets.facet import Facet


class TextualLinkFacet(Facet[str | Text]):
    """Render a link within a Textual app."""

    def show(self) -> str | Text:
        """Render the link, or literal text, whatever."""
        if isinstance(self.iri, Literal):
            return Text(self.iri, style=Style(color='grey37'))

        label = self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/env/title')],
        )

        return f'[@click="app.goto(\'{self.iri}\')"]{label}[/]'
