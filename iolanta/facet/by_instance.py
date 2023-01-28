from functools import cached_property
from typing import Optional, cast

from more_itertools import first
from rdflib.term import URIRef

from iolanta.facet.base import FacetSearchAttempt


class FindFacetByInstance(FacetSearchAttempt):
    """
    Find facet by direct link.

    Look for such `?facet` that `{self.node}` `iolanta:facet` `?facet`, whereas
    `?facet` `iolanta:supports` `{self.environment}`.
    """

    @cached_property
    def facet(self) -> Optional[URIRef]:
        """Find facet."""
        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $node iolanta:facet ?facet .
                ?facet iolanta:supports $env .
            }
            ''',
            node=self.node,
            env=self.environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except (ValueError, TypeError):
            return None
