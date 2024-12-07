from dataclasses import dataclass
from typing import Optional

from documented import DocumentedError
from rdflib.term import Node

from iolanta.models import LDContext


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


@dataclass
class UnresolvedIRI(DocumentedError):
    """
    An unresolved IRI found.

        IRI: {self.iri}
        file: {self.file}
        prefix: {self.prefix}

    Perhaps you forgot to import appropriate context? For example:

    ```yaml
    "@context":
        - {self.prefix}: https://example.com/{self.prefix}/
    ```

    Context: {self.context}
    """

    iri: str
    prefix: str
    file: Optional[str] = None    # noqa: WPS110
    context: Optional[LDContext] = None
