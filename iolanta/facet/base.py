from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from documented import Documented
from rdflib.term import Node, URIRef

from ldflex import LDFlex


@dataclass
class FacetSearchAttempt(Documented):
    """Find facet for a node."""

    ldflex: LDFlex
    node: Node
    environment: URIRef

    @cached_property
    def facet(self) -> Optional[URIRef]:
        """Find facet."""
        raise NotImplementedError()

    def __bool__(self):
        """Find if facet was found or not."""
        return self.facet is not None
