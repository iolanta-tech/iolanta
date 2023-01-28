from abc import ABC, abstractmethod

import rdflib


class GraphProvider(ABC):
    """
    Graph provider.

    Out of the blue, a graph provider returns a graph that iolanta is going to
    work off of.
    """

    @abstractmethod
    def retrieve_graph(self) -> rdflib.Dataset:
        """Find the graph."""
