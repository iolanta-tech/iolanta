from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional

import funcy
from more_itertools import first
from rdflib.term import URIRef

from iolanta.facet.base import FacetSearchAttempt
from iolanta.facet.errors import MultipleFacetsFoundForTypes

QUERY = (
    Path(__file__).parent / 'sparql/find_facet_by_instance_types.sparql'
).read_text()


@dataclass
class FindFacetByInstanceTypes(FacetSearchAttempt):
    """Find facet by node type."""

    @cached_property
    def facet(self) -> Optional[URIRef]:
        """Find facet."""
        rows = self.ldflex.query(
            QUERY,
            env=self.environment,
            node=self.node,
        )

        facets = list(set(funcy.pluck('facet', rows)))

        if len(facets) > 1:
            raise MultipleFacetsFoundForTypes(
                node=self.node,
                types=list(funcy.pluck('type', rows)),
                facets=facets,
            )

        return first(facets, None)
