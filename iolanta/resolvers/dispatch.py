from typing import Type

from rdflib import URIRef
from yarl import URL

from iolanta import Facet
from iolanta.resolvers.base import Resolver


class SchemeDispatchResolver(Resolver):
    """
    A resolver that dispatches to other resolvers based on URI scheme.

    For example, 'pkg:' URIs are handled by PyPIResolver, while
    'python:' URIs are handled by PythonImportResolver.
    """

    def __init__(self, **resolver_by_scheme: Type[Resolver]):
        """
        Initialize with a mapping of URI schemes to resolver classes.

        Args:
            **resolver_by_scheme: Mapping of URI schemes to resolver classes.
                For example: python=PythonImportResolver.
        """
        self.resolver_by_scheme = resolver_by_scheme

    def resolve(self, uri: URIRef) -> Type[Facet]:
        """
        Find a resolver by IRI, dispatching to the appropriate scheme handler.

        Args:
            uri: The URI to resolve.

        Returns:
            Facet class resolved by the appropriate scheme handler.
        """
        url = URL(uri)
        resolver_class = self.resolver_by_scheme[url.scheme]
        resolver = resolver_class()
        return resolver.resolve(uri)
