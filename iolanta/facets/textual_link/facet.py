from rdflib import Literal, URIRef
from rich.style import Style
from rich.text import Text

from iolanta.facets.facet import Facet
from iolanta.namespaces import DATATYPES


class TextualLinkFacet(Facet[str | Text]):
    """Render a link within a Textual app."""

    def show(self) -> str | Text:
        """Render the link, or literal text, whatever."""
        if isinstance(self.this, Literal):
            return f'[b grey37]{self.this}[/b grey37]'

        label = self.render(
            self.this,
            as_datatype=DATATYPES.title,
        )

        invocation = f"app.goto('{self.this}')"
        return f'[@click="{invocation}"]{label}[/]'
