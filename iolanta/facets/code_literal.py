from dataclasses import dataclass

from documented import DocumentedError
from rdflib import Literal
from rdflib.term import Node

from iolanta.facet import Facet
from iolanta.facets.bool_literal import NotALiteral


class CodeLiteral(Facet):
    """Render code strings."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.iri, Literal):
            raise NotALiteral(
                node=self.iri,
            )

        return f'<code>{self.iri.value}</code>'
