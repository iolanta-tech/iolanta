from dataclasses import dataclass, field
from typing import List

from rdflib.term import Node


@dataclass
class Stack:
    node: Node
    facet: 'iolanta.facets.facet.Facet'
    children: List['Stack'] = field(default_factory=list)
