from dataclasses import dataclass

from documented import DocumentedError

from iolanta.graph_providers.base import GraphProvider


@dataclass
class GraphCannotBeProvided(DocumentedError):
    """
    Graph cannot be provided.

        - Provider: {self.provider}
        - Error: {self.error}
    """

    provider: GraphProvider
    error: Exception
