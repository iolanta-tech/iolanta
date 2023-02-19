from dataclasses import dataclass, field

from documented import DocumentedError
from rdflib.term import Node


@dataclass
class InsufficientDataForRender(DocumentedError):
    """
    Insufficient data for rendering {self.node} — will try & download something.
    """

    node: Node
    iolanta: 'iolanta.Iolanta'

    @property
    def is_hopeless(self) -> bool:
        hopeless = self.node in self.iolanta.could_not_retrieve_nodes

        if hopeless:
            self.iolanta.logger.error(
                '%s could not be rendered, we could not retrieve describing '
                'data '
                'from the Web.',
                self.node,
            )

        return hopeless
