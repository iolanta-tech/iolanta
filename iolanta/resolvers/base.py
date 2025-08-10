from abc import abstractmethod
from typing import Type

from rdflib import URIRef

from iolanta.facets.facet import Facet


class Resolver:
    """Resolve facet IRIs into classes."""

    @abstractmethod
    def resolve(self, uri: URIRef) -> Type[Facet]:
        """Find a resolver by IRI."""
