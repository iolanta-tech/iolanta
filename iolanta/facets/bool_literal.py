from dataclasses import dataclass

from documented import DocumentedError
from rdflib import Literal
from rdflib.term import Node

from iolanta.facet import Facet


@dataclass
class NotALiteral(DocumentedError):
    """
    Node `{self.node}` is not a literal.

    It is in fact a `{self.node_type}`. `BoolLiteral` facet only supports RDF
    literal objects.
    """

    node: Node

    @property
    def node_type(self):
        """Node type name."""
        return self.node.__class__.__name__


class BoolLiteral(Facet):
    """Render bool values."""

    def show(self):
        """Render as icon."""
        if not isinstance(self.iri, Literal):
            raise NotALiteral(
                node=self.iri,
            )

        return '✔️' if self.iri.value else '❌'
