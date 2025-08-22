from rdflib import Literal

from iolanta.facets.errors import NotALiteral
from iolanta.facets.facet import Facet


class BoolLiteral(Facet):
    """Render bool values."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(
                node=self.this,
            )

        return '✔️' if self.this.value else '❌'
