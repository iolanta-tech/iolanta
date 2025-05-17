from dataclasses import dataclass
from functools import cached_property
from graphlib import TopologicalSorter
from typing import Iterable, List, TypedDict

import funcy
from rdflib.term import Literal, Node, URIRef
from yarl import URL

from iolanta.facets.errors import FacetNotFound
from iolanta.models import NotLiteralNode


class FoundRow(TypedDict):
    """Facet and datatype to render an IRI."""

    facet: NotLiteralNode
    output_datatype: NotLiteralNode


GET_QUERY_TO_FACET = """
SELECT ?facet ?match WHERE {
    ?facet
        iolanta:matches ?match ;
        iolanta:outputs $as_datatype .
}
"""


def reorder_rows_by_facet_preferences(   # noqa: WPS214, WPS210
    rows: list[FoundRow],
    ordering: set[tuple[URIRef, URIRef]],
) -> list[FoundRow]:
    """
    Apply a partial ordering to given rows.

    Preserve existing ordering.

    Note: I must confess I did not dive into this logic, it was what ChatGPT
    had suggested to me and it seemed working.

    To be fair, this should be understood and unit tested.
    """
    # Map each facet to its index in the original list for stable ordering
    row_index_map = {row['facet']: index for index, row in enumerate(rows)}

    # Initialize the topological sorter
    ts = TopologicalSorter()

    # Add edges to the graph based on ordering
    for before, after in ordering:
        if before in row_index_map and after in row_index_map:
            ts.add(after, before)

    # Compute the topological order
    sorted_facets = list(ts.static_order())

    # Append any remaining facets not in the ordering, preserving their original
    # order
    remaining_facets = [
        facet
        for facet in row_index_map
        if facet not in sorted_facets
    ]

    # Combine sorted and remaining facets
    final_order = sorted_facets + remaining_facets

    # Map back to rows and sort them
    return sorted(
        rows,
        key=lambda row: final_order.index(row['facet']),
    )


@dataclass
class FacetFinder:   # noqa: WPS214
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

    def by_sparql(self) -> Iterable[FoundRow]:
        """Determine facet by SHACL shape of the data."""
        if not isinstance(self.node, URIRef):
            return

        rows = self.iolanta.query(
            GET_QUERY_TO_FACET,
            as_datatype=self.as_datatype,
        )

        query_to_facet = {
            row['match']: row['facet']
            for row in rows
        }

        for query, facet in query_to_facet.items():
            # TODO: Verify that `query` is an ASK query
            is_matching = self.iolanta.query(query, this=self.node)
            if is_matching:
                yield FoundRow(facet=facet, output_datatype=self.as_datatype)

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

        rows = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?output_datatype ?facet WHERE {
                $node iolanta:facet ?facet .
                ?facet iolanta:outputs ?output_datatype .
            }
            """,
            node=self.node,
        )

        # FIXME This is probably suboptimal, why don't we use `IN output_datatypes`?
        rows = [row for row in rows if row['output_datatype'] == self.as_datatype]

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def _classes_for_node(self, node: NotLiteralNode) -> list[NotLiteralNode]:
        rows = self.iolanta.query(  # noqa: WPS462
            """
            SELECT DISTINCT ?class WHERE {
                $node
                    rdf:type / (owl:equivalentClass|^owl:equivalentClass)*
                    ?class .
            }
            """,
            node=node,
        )

        return funcy.lpluck('class', rows)

    def by_instance_facet(self) -> Iterable[FoundRow]:
        """Find facet by classes the IRI belongs to."""
        classes = self._classes_for_node(self.node)
        if not classes:
            return []

        formatted_classes = ', '.join(f'<{iri}>' for iri in classes)

        rows: list[FoundRow] = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?output_datatype ?facet WHERE {
                ?class iolanta:hasInstanceFacet ?facet .
                ?facet iolanta:outputs ?output_datatype .
                FILTER(?class IN (%s)) .
            }
            """ % formatted_classes,
            classes=classes,
            output_datatype=self.as_datatype,
        )

        return sorted(
            rows,
            key=self.row_sorter_by_output_datatype,
        )

    def by_output_datatype_default_facet(self) -> Iterable[FoundRow]:
        """Find facet based on output_datatype only."""
        rows = self.iolanta.query(
            '''
            SELECT ?facet ?output_datatype WHERE {
              $output_datatype iolanta:hasDefaultFacet ?facet .
            }
            ''',
            output_datatype=self.as_datatype,
        )

        return [
            FoundRow(facet=row['facet'], output_datatype=row['output_datatype'])
            for row in rows
        ]

    def by_facet_not_found(self) -> Iterable[FoundRow]:
        """What facet to show if no facets are found?"""
        rows = self.iolanta.query(  # noqa: WPS462
            """
            SELECT ?facet ?output_datatype WHERE {
              $output_datatype iolanta:when-no-facet-found ?facet .
            }
            """,
            output_datatype=self.as_datatype,
        )

        return [
            FoundRow(facet=row['facet'], output_datatype=row['output_datatype'])
            for row in rows
        ]

    def retrieve_facets_preference_ordering(self) -> set[tuple[URIRef, URIRef]]:
        """
        Construct partial ordering on the set of facets.

        In each pair, the first element is preferred over the latter.
        """
        rows = self.iolanta.query(  # noqa: WPS462
            """
            SELECT ?preferred ?over WHERE {
                ?preferred iolanta:is-preferred-over ?over
            }
            """,
        )

        return {
            (row['preferred'], row['over'])
            for row in rows
        }

    def choices(self) -> list[FoundRow]:
        """Return all suitable facets."""
        rows = list(self._found_facets())

        if not rows:
            rows = self.by_facet_not_found()

        if len(rows) == 1:
            # Nothing to order.
            return rows

        ordering = self.retrieve_facets_preference_ordering()
        return reorder_rows_by_facet_preferences(rows, ordering)

    @property
    def facet_and_output_datatype(self) -> FoundRow:
        """Choose the best facet for the IRI."""
        if choice := funcy.first(self.choices()):
            return choice

        raise FacetNotFound(
            node=self.node,
            as_datatype=self.as_datatype,
            node_types=[],
        )

    def _found_facets(self) -> Iterable[FoundRow]:
        """Compose a stream of all possible facet choices."""
        yield from self.by_sparql()
        yield from self.by_prefix()
        yield from self.by_datatype()
        yield from self.by_facet()
        yield from self.by_instance_facet()
        yield from self.by_output_datatype_default_facet()
