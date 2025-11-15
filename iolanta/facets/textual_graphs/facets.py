from collections import defaultdict
from pathlib import Path
from typing import Iterable, NamedTuple

import funcy
from rdflib import Literal, Node
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin


class GraphRow(NamedTuple):
    """A row in the graphs table."""

    graph: NotLiteralNode
    count: int


class GraphsTable(IolantaWidgetMixin, DataTable):
    """Render graphs as a table with graph URI and triple count."""

    BINDINGS = [
        ('enter', 'goto', 'Goto'),
    ]

    def __init__(self, rows: Iterable[GraphRow]):
        """Construct."""
        super().__init__(show_header=True, cell_padding=1)
        self.graph_rows = list(rows)

    def render_human_readable_cells(self):
        """Replace the cells with their human readable titles."""
        terms_and_coordinates = sorted(
            self.node_to_coordinates.items(),
            key=lambda node_and_coordinates_pair: len(
                node_and_coordinates_pair[1],
            ),
            reverse=True,
        )

        for term, coordinates in terms_and_coordinates:
            title = str(self.iolanta.render(term, as_datatype=DATATYPES.title))
            for coordinate in coordinates:
                self.app.call_from_thread(
                    self.update_cell_at,
                    coordinate,
                    value=title,
                    update_width=False,
                )

    @funcy.cached_property
    @funcy.post_processing(dict)
    def coordinate_to_node(self):
        """Return a mapping of coordinates to their corresponding nodes."""
        for row_number, (graph, _count) in enumerate(self.graph_rows):
            yield Coordinate(row_number, 0), graph

    @funcy.cached_property
    def node_to_coordinates(self) -> defaultdict[Node, list[Coordinate]]:
        """Map node to coordinates where it appears."""
        node_to_coordinate = [
            (node, coordinate)
            for coordinate, node in self.coordinate_to_node.items()
        ]
        return funcy.group_values(node_to_coordinate)

    def format_as_loading(self, node: Node) -> str:
        """Intermediate version of a value while it is loading."""
        if isinstance(node, Literal):
            node_text = f'⌛ {node}'
        else:
            node_text = self.iolanta.node_as_qname(node)
            node_text = f'⌛ {node_text}'

        return node_text

    def on_mount(self):
        """Fill the table and start rendering."""
        self.add_columns('Graph', 'Triples Count')
        self.cell_padding = 1

        for graph, count in self.graph_rows:
            self.add_row(
                self.format_as_loading(graph),
                str(count),
            )

        self.run_worker(
            self.render_human_readable_cells,
            thread=True,
        )

    def action_goto(self):
        """Navigate to the selected graph."""
        if self.cursor_coordinate:
            node = self.coordinate_to_node.get(self.cursor_coordinate)
            if node is not None:
                self.app.action_goto(node)


class GraphsBody(Vertical):
    """Container for graphs table."""

    DEFAULT_CSS = """
    GraphsBody {
        height: auto;
        max-height: 100%;
    }
    """


class Graphs(Facet):
    """Render named graphs as a table."""

    META = Path(__file__).parent / 'data' / 'textual_graphs.yamlld'

    def show(self):
        """Construct the table."""
        rows = self.stored_query('graphs.sparql')

        return GraphsBody(
            PageTitle(self.this),
            GraphsTable(
                [
                    GraphRow(
                        graph=row['graph'],
                        count=int(row['count'].value),
                    )
                    for row in rows
                ],
            ),
        )
