import functools

from mypy.memprofile import defaultdict
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Tree

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.models import Triple


class TriplesTree(Tree):
    """Triples as tree."""

    def __init__(self, triples: list[Triple]):
        self.triples = triples
        super().__init__(label='Triples')

        self.show_root = False
        triples_tree = defaultdict(functools.partial(defaultdict, list))
        for subject, predicate, obj in triples:
            triples_tree[subject][predicate].append(obj)

        for subject, properties in triples_tree.items():
            subject_node = self.root.add(subject, data=subject, expand=False)

            for predicate, objects in properties.items():
                predicate_node = subject_node.add(predicate, expand=True)

                for obj in objects:
                    predicate_node.add_leaf(obj)


class GraphFacet(Facet[Widget]):
    """Display triples in a graph."""

    def show(self) -> Widget:
        triples = [
            Triple(triple['subject'], triple['predicate'], triple['object'])
            for triple in self.stored_query('triples.sparql', graph=self.iri)
        ]

        tree = TriplesTree(triples)
        triple_count = len(triples)
        return Vertical(
            PageTitle(self.iri, extra=f'({triple_count} triples)'),
            tree,
        )
