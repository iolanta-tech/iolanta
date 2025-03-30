from typing import Iterable

import funcy
from rdflib.term import Literal, Node
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from iolanta import Facet
from iolanta.facets.textual_nanopublication.term_widget import TermWidget
from iolanta.models import Triple
from iolanta.widgets.mixin import IolantaWidgetMixin

BACKGROUND_COLORS = [    # noqa: WPS407
    # Let's honor 🇦🇲 flag!
    'darkred',
    'darkblue',
    'darkorange',

    'darkcyan',
    'darkgoldenrod',
    # 'darkgray',
    'darkgreen',
    # 'darkgrey',
    'darkkhaki',
    'darkmagenta',
    'darkolivegreen',
    'darkorchid',
    'darksalmon',
    'darkseagreen',
    # 'darkslateblue',
    # 'darkslategray',
    # 'darkslategrey',
    'darkturquoise',
    'darkviolet',
]


class TripleView(IolantaWidgetMixin, Horizontal):
    """Display a triple."""

    DEFAULT_CSS = """
    TripleView {
        padding-left: 0;
        padding-top: 0;
        padding-bottom: 1;
        height: auto;
    }
    """

    def __init__(
        self,
        triple: Triple,
        color_per_node: dict[Node, str] | None = None,
    ):
        """Initialize."""
        self.triple = triple
        self.color_per_node = color_per_node
        super().__init__()

    def compose(self):
        """Render the triple."""
        for term in self.triple:   # noqa: WPS526
            yield TermWidget(
                term,
                background_color=self.color_per_node.get(term),
            )


def construct_color_per_node(nodes: Iterable[Node]) -> dict[Node, str]:
    """Distribute rainbow colors over the nodes and choose a color for each."""
    non_literal_nodes = filter(
        lambda node: not isinstance(node, Literal),
        nodes,
    )

    distinct_nodes = funcy.ldistinct(non_literal_nodes)

    return funcy.zipdict(
        distinct_nodes,
        funcy.cycle(BACKGROUND_COLORS),
    )


class TriplesView(IolantaWidgetMixin, Vertical):
    """Display a set of triples."""

    DEFAULT_CSS = """
    TriplesView {
        padding: 1 2;
        height: auto;
    }
    """

    def __init__(self, triples: Iterable[Triple]):
        """Initialize."""
        self.triples = triples
        self.color_per_node = construct_color_per_node(
            [
                term
                for triple in triples
                for term in triple
            ],
        )
        super().__init__()

    def compose(self):
        """Mount the triple stubs."""
        for triple in self.triples:   # noqa: WPS526
            yield TripleView(triple, color_per_node=self.color_per_node)

    def on_mount(self):
        """Initialize triples rendering."""
        self.run_worker(self.render_triples, thread=True)

    def render_triples(self):
        """Render triples."""
        term_view: TermWidget
        triple_view: TripleView
        for triple_view in self.children:
            for term_view in triple_view.children:
                term_view.renderable = self.iolanta.render(
                    term_view.uri,
                    as_datatype=term_view.as_datatype,
                )


class GraphTriplesFacet(Facet[Widget]):
    """Render a graph as triples."""

    def show(self) -> Widget:
        """Render a graph as triples."""
        rows = self.query(  # noqa: WPS462
            """
            SELECT ?subject ?predicate ?object WHERE {
                GRAPH $graph {
                    ?subject ?predicate ?object .
                }
            }
            ORDER BY ?subject ?predicate ?object
            """,
            graph=self.iri,
        )

        triples = [
            Triple(
                subject=row['subject'],
                predicate=row['predicate'],
                object=row['object'],
            )
            for row in rows
        ]

        return TriplesView(triples)
