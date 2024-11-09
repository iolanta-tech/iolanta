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

    def __init__(self, triples: list[Triple]):   # noqa: WPS210
        """Initialize the tree."""
        self.triples = triples
        super().__init__(label='Triples')

        self.show_root = False
        triples_tree = self._construct_triples_tree(triples)

        for subject, properties in triples_tree.items():
            subject_node = self.root.add(subject, data=subject, expand=False)

            for predicate, obj_nodes in properties.items():
                predicate_node = subject_node.add(predicate, expand=True)

                for obj_node in obj_nodes:
                    predicate_node.add_leaf(obj_node)

    def _construct_triples_tree(self, triples):
        triples_tree = defaultdict(functools.partial(defaultdict, list))
        for subject, predicate, object_node in triples:
            triples_tree[subject][predicate].append(object_node)
        return triples_tree


class GraphFacet(Facet[Widget]):
    """Display triples in a graph."""

    def show(self) -> Widget:
        """Show the widget."""
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
