from collections import defaultdict
from typing import Iterable

import funcy
from rdflib import Literal, Node
from rich.style import Style
from rich.text import Text
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.widgets import DataTable

from iolanta import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin

PAIRS_QUERY = """
SELECT ?subject ?object WHERE {
    ?subject $this ?object .
} ORDER BY ?subject ?object
"""


class PairsTable(IolantaWidgetMixin, DataTable):
    """Render subject → object properties as a table with two columns."""

    BINDINGS = [
        ('enter', 'goto', 'Goto'),
    ]

    def __init__(self, pairs: Iterable[tuple[NotLiteralNode, Node]]):
        """Construct."""
        super().__init__(show_header=False, cell_padding=1)
        self.pairs = list(pairs)

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
            title = self.iolanta.render(term, as_datatype=DATATYPES.title)
            for coordinate in coordinates:
                self.app.call_from_thread(
                    self.update_cell_at,
                    coordinate,
                    value=Text(title, no_wrap=False),
                    update_width=False,
                )

    @funcy.cached_property
    @funcy.post_processing(dict)
    def coordinate_to_node(self):
        """Return a mapping of coordinates to their corresponding nodes."""
        for row_number, (subject, object_term) in enumerate(self.pairs):
            yield Coordinate(row_number, 0), subject
            yield Coordinate(row_number, 1), object_term

    @funcy.cached_property
    def node_to_coordinates(self) -> defaultdict[Node, list[Coordinate]]:
        """Map node to coordinates where it appears."""
        node_to_coordinate = [
            (node, coordinate)
            for coordinate, node in self.coordinate_to_node.items()
        ]
        return funcy.group_values(node_to_coordinate)

    def format_as_loading(self, node: Node) -> Text:
        """Intermediate version of a value while it is loading."""
        if isinstance(node, Literal):
            node_text = f'⌛ {node}'
        else:
            node_text = self.iolanta.node_as_qname(node)
            node_text = f'⌛ {node_text}'

        return Text(
            node_text,
            style=Style(dim=True),
            no_wrap=False,
        )

    def on_mount(self):
        """Fill the table and start rendering."""
        self.add_columns('Subject', 'Object')
        self.cell_padding = 1

        for subject, object_term in self.pairs:
            self.add_row(
                self.format_as_loading(subject),
                self.format_as_loading(object_term),
            )

        self.run_worker(
            self.render_human_readable_cells,
            thread=True,
        )

    def action_goto(self):
        """Navigate to the selected node."""
        if self.cursor_coordinate:
            node = self.coordinate_to_node.get(self.cursor_coordinate)
            if node is not None:
                self.app.action_goto(node)


class TextualPropertyPairsTableFacet(Facet):
    """Render a table of subject → object pairs for a property."""

    def show(self):
        """Construct the table."""
        rows = self.query(
            PAIRS_QUERY,
            this=self.this,
        )

        return Vertical(
            PageTitle(
                self.this,
                extra='— Subjects & Objects connected by this property',
            ),
            PairsTable(
                [
                    (row['subject'], row['object'])
                    for row in rows
                ],
            ),
        )
