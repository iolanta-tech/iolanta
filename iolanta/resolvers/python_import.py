from typing import Type

from rdflib import URIRef

from iolanta.facets.facet import Facet
from iolanta.resolvers.base import Resolver


class PythonImportResolver(Resolver):
    """Resolve facet IRIs into classes by importing Python modules."""

    def resolve(self, uri: URIRef) -> Type[Facet]:
        """Find a resolver by IRI in python:<module>.<class> format."""
        raise NotImplementedError(
            f'{uri} URL for facet import is unsupported anymore '
            f'due to security reasons.',
        )
