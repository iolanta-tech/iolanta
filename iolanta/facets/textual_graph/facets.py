import functools
from dataclasses import dataclass
from typing import ClassVar

from mypy.memprofile import defaultdict
from rdflib.term import Literal, Node
from rich.text import Text
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.iolanta import Iolanta
from iolanta.models import Triple
from iolanta.namespaces import DATATYPES


@dataclass
class TreeNodeData:
    """Data attached to a tree node."""

    node: Node
    is_rendered: bool = False


class TriplesTree(Tree):   # noqa: WPS214
    """Triples as tree."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
    ]

    def __init__(  # noqa: WPS210
        self,
        triples: list[Triple],
        iolanta: Iolanta,
    ):   # noqa: WPS210
        """Initialize the tree."""
        self.triples = triples
        self.iolanta = iolanta
        self.selected_node = None
        super().__init__(label='Triples')

        self.show_root = False
        triples_tree = self._construct_triples_tree(triples)

        for subject, properties in triples_tree.items():
            subject_node = self.root.add(
                self._format_not_rendered_iri(subject),
                data=TreeNodeData(subject),
                expand=False,
            )

            for predicate, obj_nodes in properties.items():
                predicate_node = subject_node.add(
                    self._format_not_rendered_iri(predicate),
                    data=TreeNodeData(predicate),
                    expand=True,
                )

                for obj_node in obj_nodes:
                    predicate_node.add_leaf(
                        self._format_not_rendered_iri(obj_node),
                        data=TreeNodeData(obj_node),
                    )

    def on_mount(self):
        """Trigger rendering of titles asynchronously."""
        self.run_worker(
            functools.partial(
                self.render_titles_for_children,
                self.root,
            ),
            thread=True,
        )

    def render_titles_for_children(
        self,
        node: TreeNode[TreeNodeData],
        recursive: bool = False,
    ):
        """Render titles for children."""
        for child in node.children:
            if child.data.is_rendered:
                continue

            iri = child.data.node
            if isinstance(iri, Literal):
                label = self._format_not_rendered_iri(iri)
            else:
                label = self.iolanta.render(
                    iri,
                    as_datatype=DATATYPES.title,
                )[0]

            self.app.call_from_thread(
                child.set_label,
                label,
            )

            child.data.is_rendered = True

            if recursive:
                self.render_titles_for_children(child, recursive=True)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded[Node]):
        """Render titles of children when node is expanded."""
        self.run_worker(
            functools.partial(
                self.render_titles_for_children,
                event.node,
                recursive=True,
            ),
            thread=True,
        )

    def on_tree_node_selected(self, event: Tree.NodeSelected[TreeNodeData]):
        """Handle node selection."""
        self.selected_node = event.node

    def action_goto(self) -> None:
        """Navigate to the selected node."""
        if self.selected_node:
            self.app.action_goto(self.selected_node.data.node)

    def _format_not_rendered_iri(self, node: Node):
        return Text(str(node), style='#696969')

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

        tree = TriplesTree(triples=triples, iolanta=self.iolanta)
        triple_count = len(triples)
        return Vertical(
            PageTitle(self.iri, extra=f'({triple_count} triples)'),
            tree,
        )
