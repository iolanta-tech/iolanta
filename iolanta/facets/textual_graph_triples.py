from collections.abc import Callable, Iterable, Mapping
from typing import cast

import funcy
from rdflib.term import Literal, Node, URIRef
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from iolanta import Facet
from iolanta.facets.textual_nanopublication.term_widget import TermWidget
from iolanta.models import NotLiteralNode, Triple
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin

BACKGROUND_COLORS = [  # noqa: WPS407
    # Let's honor 🇦🇲 flag!
    "darkred",
    "darkblue",
    "darkorange",
    "darkcyan",
    "darkgoldenrod",
    # 'darkgray',
    "darkgreen",
    # 'darkgrey',
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorchid",
    "darksalmon",
    "darkseagreen",
    # 'darkslateblue',
    # 'darkslategray',
    # 'darkslategrey',
    "darkturquoise",
    "darkviolet",
]


class TripleView(IolantaWidgetMixin, Horizontal):
    """Display a triple."""

    DEFAULT_CSS = """  # noqa: WPS115
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
        self.color_per_node = color_per_node or {}
        super().__init__()

    def compose(self):
        """Render the triple."""
        for term in self.triple:  # noqa: WPS526
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


def is_informative_triple(
    triple: Triple,
    render_title: Callable[[Node], object],
) -> bool:
    """Check whether a triple adds visible information to the graph view."""
    if not isinstance(triple.object, Literal):
        return True

    return str(render_title(triple.subject)) != str(render_title(triple.object))


class TriplesView(IolantaWidgetMixin, Vertical):
    """Display a set of triples."""

    DEFAULT_CSS = """  # noqa: WPS115
    TriplesView {
        padding: 1 2;
        height: auto;
    }
    """

    def __init__(self, triples: Iterable[Triple]):
        """Initialize."""
        self.triples = triples
        self.color_per_node = construct_color_per_node(
            [term for triple in triples for term in triple],
        )
        super().__init__()

    def compose(self):
        """Mount the triple stubs."""
        for triple in self.triples:  # noqa: WPS526
            yield TripleView(triple, color_per_node=self.color_per_node)

    def on_mount(self):
        """Initialize triples rendering."""
        self.run_worker(self.render_triples, thread=True)

    def render_triples(self):
        """Render triples."""
        for term_view in self._term_widgets():
            term_view.renderable = self.iolanta.render(
                term_view.uri,
                as_datatype=term_view.as_datatype,
            )

    def _triple_views(self) -> Iterable[TripleView]:
        """Iterate over mounted triple views."""
        for child in self.children:
            if isinstance(child, TripleView):
                yield child

    def _term_widgets(self) -> Iterable[TermWidget]:
        """Iterate over mounted term widgets."""
        for triple_view in self._triple_views():
            for child in triple_view.children:
                if isinstance(child, TermWidget):
                    yield child


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
            graph=self.this,
        )
        triple_rows = cast(Iterable[Mapping[str, Node]], rows)

        triples = [
            Triple(
                subject=cast(NotLiteralNode, row["subject"]),
                predicate=cast(NotLiteralNode, row["predicate"]),
                object=cast(URIRef | Literal, row["object"]),
            )
            for row in triple_rows
        ]

        informative_triples = [
            triple
            for triple in triples
            if is_informative_triple(
                triple=triple,
                render_title=self._render_title,
            )
        ]

        return TriplesView(informative_triples)

    def _render_title(self, node: Node) -> object:
        """Render node title."""
        return self.render(node, as_datatype=DATATYPES.title)
