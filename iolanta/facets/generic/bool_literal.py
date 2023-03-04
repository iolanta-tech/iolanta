from rdflib import Literal

from iolanta.facets.errors import NotALiteral
from iolanta.facets.facet import Facet


class BoolLiteral(Facet):
    """Render bool values."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.iri, Literal):
            raise NotALiteral(
                node=self.iri,
            )

        return '✔️' if self.iri.value else '❌'
