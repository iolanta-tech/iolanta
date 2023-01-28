from functools import cached_property
from typing import Optional, cast

from more_itertools import first
from rdflib.term import URIRef

from iolanta.facet.base import FacetSearchAttempt


class FindFacetByEnvironment(FacetSearchAttempt):
    """
    Find facet by environment.

    Look for such `?facet` that `{self.environment}` `iolanta:hasDefaultFacet`
    `?facet`.
    """

    @cached_property
    def facet(self) -> Optional[URIRef]:
        """Find facet."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $env iolanta:hasDefaultFacet ?facet .
            }
            ''',
            env=self.environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except (ValueError, TypeError):
            return None
