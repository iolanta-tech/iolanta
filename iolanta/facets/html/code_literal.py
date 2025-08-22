from rdflib import Literal

from iolanta.facets.errors import NotALiteral
from iolanta.facets.facet import Facet


class CodeLiteral(Facet):
    """Render code strings."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(
                node=self.this,
            )

        return f'<code>{self.this.value}</code>'
