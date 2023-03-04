from rdflib import Literal

from iolanta.facets.bool_literal import NotALiteral
from iolanta.facets.facet import Facet


class CodeLiteral(Facet):
    """Render code strings."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.iri, Literal):
            raise NotALiteral(
                node=self.iri,
            )

        return f'<code>{self.iri.value}</code>'
