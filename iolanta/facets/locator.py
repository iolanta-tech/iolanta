from dataclasses import dataclass, field
from functools import cached_property
from typing import Dict, Iterable, List, Optional, Type, TypedDict

import funcy
from rdflib import ConjunctiveGraph
from rdflib.term import Literal, Node, URIRef
from yarl import URL

from iolanta.facets.errors import FacetNotFound
from iolanta.models import NotLiteralNode
from iolanta.namespaces import IOLANTA


class FoundRow(TypedDict):
    facet: NotLiteralNode
    as_datatype: NotLiteralNode


@dataclass
class FacetFinder:
    """Engine to find facets for a given node."""

    iolanta: 'iolanta.Iolanta'    # type: ignore
    node: Node
    as_datatype: NotLiteralNode

    @cached_property
    def row_sorter_by_output_datatype(self):
        def _sorter(row) -> int:
            return 0

        return _sorter

    def by_datatype(self) -> Iterable[FoundRow]:
        if not isinstance(self.node, Literal):
            return []

        if (data_type := self.node.datatype) is None:
            return []

        rows = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?output_datatype ?facet WHERE {
                $data_type iolanta:hasDatatypeFacet ?facet .
                ?facet iolanta:outputs ?output_datatype .
            }
            """,
            data_type=data_type,
        )

        rows = [row for row in rows if row['output_datatype'] == self.as_datatype]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def by_prefix(self) -> Iterable[FoundRow]:
        """Determine facet by URL prefix.

        TODO fix this to allow arbitrary prefixes.
        """
        scheme = URL(self.node).scheme
        if scheme != 'urn':
            return []

        if not isinstance(self.node, URIRef):
            return []

        rows = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?output_datatype ?facet WHERE {
                $prefix iolanta:hasFacetByPrefix ?facet .
                ?facet iolanta:outputs ?output_datatype .
            }
            """,
            prefix=URIRef(f'{scheme}:'),
        )

        rows = [row for row in rows if row['output_datatype'] == self.as_datatype]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def by_facet(self) -> List[FoundRow]:
        """Find a facet directly attached to the node."""
        if isinstance(self.node, Literal):
            return []

        rows = self.iolanta.query(
            '''
            SELECT ?output_datatype ?facet WHERE {
                $node iolanta:facet ?facet .
                ?facet iolanta:outputs ?output_datatype .
            }
            ''',
            node=self.node,
        )

        # FIXME This is probably suboptimal, why don't we use `IN output_datatypes`?
        rows = [row for row in rows if row['output_datatype'] == self.as_datatype]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def by_instance_facet(self) -> Iterable[FoundRow]:
        rows = self.iolanta.query(
            '''
            SELECT ?output_datatype ?facet WHERE {
                $node a ?class .
                ?class iolanta:hasInstanceFacet ?facet .
                ?facet iolanta:outputs ?output_datatype .
            }
            ''',
            node=self.node,
        )

        rows = [row for row in rows if row['output_datatype'] == self.as_datatype]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def by_output_datatype_default_facet(self) -> Iterable[FoundRow]:
        """Find facet based on output_datatype only."""
        graph: ConjunctiveGraph = self.iolanta.graph

        triples = graph.triples(     # type: ignore
            (None, IOLANTA.hasDefaultFacet, None),
        )
        triples = [
            triple
            for triple in triples
            if funcy.first(triple) == self.as_datatype
        ]

        rows = [
            {
                'facet': facet,
                'output_datatype': output_datatype,
            } for output_datatype, _, facet in triples
        ]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    @funcy.post_processing(list)
    def choices(self) -> Iterable[FoundRow]:
        """Compose a stream of all possible facet choices."""
        yield from self.by_prefix()
        yield from self.by_datatype()
        yield from self.by_facet()
        yield from self.by_instance_facet()
        yield from self.by_output_datatype_default_facet()

    @property
    def facet_and_output_datatype(self) -> FoundRow:
        if choice := funcy.first(self.choices()):
            return choice

        raise FacetNotFound(
            node=self.node,
            as_datatype=self.as_datatype,
            node_types=[],
        )
