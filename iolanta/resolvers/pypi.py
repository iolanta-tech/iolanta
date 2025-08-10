from __future__ import annotations

import re
from importlib import metadata
from typing import Type

from packageurl import PackageURL
from rdflib import URIRef

from iolanta import Facet
from iolanta.resolvers.base import Resolver

ENTRY_POINT_GROUP = 'iolanta.facets'


def _norm(name: str) -> str:
    """Normalize package name by replacing common separators with dashes."""
    return re.sub('[-_.]+', '-', name).lower()


class MissingFacetError(RuntimeError):
    """Raised when a required facet is not found in the installed packages."""


class PyPIResolver(Resolver):
    """Resolve facet IRIs into classes from PyPI packages."""

    def resolve(self, uri: URIRef) -> Type[Facet]:
        """Find and load a Facet class from a PyPI package."""
        dist_name, facet_name = self._get_package_info(uri)
        dist = self._get_distribution(dist_name, facet_name)
        entry_point = self._find_facet_entry_point(dist, facet_name)
        facet_class = entry_point.load()
        self._validate_facet_class(
            facet_class=facet_class,
            facet_name=facet_name,
            dist_name=dist.metadata['Name'],
        )
        return facet_class

    def _get_package_info(self, uri: URIRef) -> tuple[str, str]:
        """Extract and validate package information from URI."""
        package_url = PackageURL.from_string(str(uri))
        if package_url.type != 'pypi':
            raise NotImplementedError(f'{package_url.type} is not supported')

        dist_name = _norm(package_url.name or '')
        facet_name = package_url.subpath

        if not dist_name or not facet_name:
            raise ValueError('PURL must be pkg:pypi/<dist>#<FacetName>')

        return dist_name, facet_name

    def _get_distribution(
        self,
        dist_name: str,
        facet_name: str,
    ) -> metadata.Distribution:
        """Get package distribution and verify it exists."""
        try:
            return metadata.distribution(dist_name)
        except metadata.PackageNotFoundError as exc:
            raise MissingFacetError(
                f'This page requires `{dist_name}` (facet `{facet_name}`). '
                f'Install with: pip install "{dist_name}"',
            ) from exc

    def _find_facet_entry_point(
        self,
        dist: metadata.Distribution,
        facet_name: str,
    ) -> metadata.EntryPoint:
        """Find the facet entry point in the distribution."""
        matching_entry_points = [
            entry_point
            for entry_point in dist.entry_points
            if (
                entry_point.group == ENTRY_POINT_GROUP
                and entry_point.name == facet_name
            )
        ]

        if not matching_entry_points:
            dist_name = dist.metadata['Name']
            msg = (
                f'Facet `{facet_name}` not found in `{dist_name}` '
                f'{dist.version}. Ensure it exposes entry point '
                f'`{ENTRY_POINT_GROUP}` named `{facet_name}`.'
            )
            raise MissingFacetError(msg)

        return matching_entry_points[0]

    def _validate_facet_class(
        self,
        facet_class: Type[Facet],
        facet_name: str,
        dist_name: str,
    ) -> None:
        """Validate that the loaded class is a Facet subclass."""
        if not issubclass(facet_class, Facet):
            raise TypeError(
                f'Entry point `{facet_name}` in `{dist_name}` '
                'is not a subclass of iolanta.Facet',
            )
