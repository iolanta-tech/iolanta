from dataclasses import dataclass, field
from functools import cached_property
from typing import Dict, List, Optional, Type, TypedDict, Iterable

import funcy
from rdflib import ConjunctiveGraph
from rdflib.term import Literal, Node, URIRef

from iolanta.facets.errors import FacetNotFound
from iolanta.models import NotLiteralNode
from iolanta.namespaces import IOLANTA


class FoundRow(TypedDict):
    facet: NotLiteralNode
    environment: NotLiteralNode


@dataclass
class FacetFinder:
    """Engine to find facets for a given node."""

    iolanta: 'iolanta.Iolanta'    # type: ignore
    node: Node
    environments: List[NotLiteralNode]

    @cached_property
    def row_sorter_by_environment(self):
        def _sorter(row) -> int:
            return self.environments.index(row['environment'])

        return _sorter

    def by_datatype(self) -> Iterable[FoundRow]:
        if not isinstance(self.node, Literal):
            return []

        if (data_type := self.node.datatype) is None:
            return []

        rows = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?environment ?facet WHERE {
                $data_type iolanta:hasDatatypeFacet ?facet .
                ?facet iolanta:supports ?environment .
            }
            """,
            data_type=data_type,
        )

        rows = [row for row in rows if row['environment'] in self.environments]

        return sorted(
            rows,
            key=self.row_sorter_by_environment,
        )

    def by_facet(self) -> List[FoundRow]:
        if isinstance(self.node, Literal):
            return []

        rows = self.iolanta.query(
            '''
            SELECT ?environment ?facet WHERE {
                $node iolanta:facet ?facet .
                ?facet iolanta:supports ?environment .
            }
            ''',
            node=self.node,
        )

        # FIXME This is probably suboptimal, why don't we use `IN environments`?
        rows = [row for row in rows if row['environment'] in self.environments]

        return sorted(
            rows,
            key=self.row_sorter_by_environment,
        )

    def by_instance_facet(self) -> Iterable[FoundRow]:
        rows = self.iolanta.query(
            '''
            SELECT ?environment ?facet WHERE {
                $node a ?class .
                ?class iolanta:hasInstanceFacet ?facet .
                ?facet iolanta:supports ?environment .
            }
            ''',
            node=self.node,
        )

        rows = [row for row in rows if row['environment'] in self.environments]

        return sorted(
            rows,
            key=self.row_sorter_by_environment,
        )

    def by_environment_default_facet(self) -> Iterable[FoundRow]:
        """Find facet based on environment only."""
        graph: ConjunctiveGraph = self.iolanta.graph

        triples = graph.triples(     # type: ignore
            (None, IOLANTA.hasDefaultFacet, None),
        )
        triples = [
            triple
            for triple in triples
            if funcy.first(triple) in self.environments
        ]

        rows = [
            {
                'facet': facet,
                'environment': environment,
            } for environment, _, facet in triples
        ]

        return sorted(
            rows,
            key=self.row_sorter_by_environment,
        )

    def choices(self) -> Iterable[FoundRow]:
        yield from self.by_datatype()
        yield from self.by_facet()
        yield from self.by_instance_facet()
        yield from self.by_environment_default_facet()

    @property
    def facet_and_environment(self) -> FoundRow:
        if choice := funcy.first(self.choices()):
            return choice

        raise FacetNotFound(
            node=self.node,
            environments=self.environments,
            node_types=[],
        )
