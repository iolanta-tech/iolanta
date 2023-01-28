from functools import cached_property
from typing import Optional, cast

from more_itertools import first
from rdflib.term import Literal, URIRef

from iolanta.facet.base import FacetSearchAttempt


class FindFacetByLiteralDatatype(FacetSearchAttempt):
    """
    Find facet for a literal value by data type.

    Look for such `?facet` that `{self.node.datatype}` `iolanta:datatypeFacet`
    `?facet`, whereas `?facet` `iolanta:supports` `{self.environment}`.
    """

    @cached_property
    def facet(self) -> Optional[URIRef]:
        """Find facet."""
        if not isinstance(self.node, Literal):
            return None

        if (datatype := self.node.datatype) is None:
            return None

        rows = self.ldflex.query(
            '''
            SELECT ?facet WHERE {
                $datatype iolanta:datatypeFacet ?facet .
                ?facet iolanta:supports $env .
            }
            ''',
            datatype=datatype,
            env=self.environment,
        )

        try:
            return cast(URIRef, first(rows)['facet'])
        except ValueError:
            return None
