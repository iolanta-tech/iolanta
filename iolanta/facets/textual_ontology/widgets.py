import hashlib

from rdflib.term import Node
from textual import events
from textual.containers import (
    Horizontal,
    VerticalGroup,
    VerticalScroll,
)
from textual.widgets import Static

from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin

# Column-count math: cell width plus inter-slot spacing.
# Keep `TERM_CARD_ROW_GAP` aligned with TermCardRow child margin-right.
TERM_CARD_MIN_COLUMN_WIDTH = 22
TERM_CARD_ROW_GAP = 2
TERM_CARD_ROWSTACK_WIDTH_RETRIES = 32

# Terminal named colors; aligned with ``BACKGROUND_COLORS`` in textual graph triples.
_TERM_CARD_BACKGROUND_PALETTE: tuple[str, ...] = (
    'darkred',
    'darkblue',
    'darkorange',
    'darkcyan',
    'darkgoldenrod',
    'darkgreen',
    'darkkhaki',
    'darkmagenta',
    'darkolivegreen',
    'darkorchid',
    'darksalmon',
    'darkseagreen',
    'darkturquoise',
    'darkviolet',
)


def _term_card_background_color(term: Node) -> str:
    """Map a term to a palette entry (stable across runs, spread across vocabulary).

    Uses SHA-256 of ``str(term)`` so the same IRI or blank node id always gets the
    same swatch. Alternatives: cycle colors in facet traversal order (like
    ``construct_color_per_node`` in ``textual_graph_triples``), or RDF metadata
    if the vocabulary exposes a color property.
    """
    digest = hashlib.sha256(str(term).encode()).digest()
    slot = int.from_bytes(digest[:8], 'big') % len(_TERM_CARD_BACKGROUND_PALETTE)
    return _TERM_CARD_BACKGROUND_PALETTE[slot]


class TermsContent(VerticalScroll):
    """Display grouped list of terms."""

    DEFAULT_CSS = """
    TermsContent {
        padding-top: 1;
        padding-bottom: 1;
        padding-left: 1;
        padding-right: 2;
    }
    """  # noqa: WPS115


class TermCard(IolantaWidgetMixin, Static):
    """Card for one ontology term: title only; whole surface opens the term.

    Background color is chosen by ``_term_card_background_color`` (hash → palette).
    """

    DEFAULT_CSS = """
    TermCard {
        border: none;
        outline: none;
        padding-top: 2;
        padding-right: 2;
        padding-bottom: 1;
        padding-left: 1;
        text-align: right;
        width: 1fr;
        height: auto;
        color: $text;
        text-style: none;
    }
    TermCard:hover {
        background-tint: $foreground 10%;
    }
    """  # noqa: WPS115

    def __init__(self, term: Node) -> None:
        self._term = term
        super().__init__("")
        self.styles.background = _term_card_background_color(term)

    def on_mount(self) -> None:
        label = self.iolanta.render(self._term, as_datatype=DATATYPES.title)
        self.update(label)

    def on_click(self, _event: events.Click) -> None:
        self.app.action_goto(self._term)


class TermCardSlot(Static):
    """Invisible cell: pads a row so column widths match other groups."""

    DEFAULT_CSS = """
    TermCardSlot {
        width: 1fr;
        height: auto;
        min-height: 1;
    }
    """  # noqa: WPS115


class TermCardRow(Horizontal):
    """One row of cards; use margins for spacing (no horizontal `gap`)."""

    DEFAULT_CSS = """
    TermCardRow {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }
    TermCardRow > * {
        margin-right: 2;
    }
    """  # noqa: WPS115


class TermCardRowStack(VerticalGroup):
    """Rows of cards; column count follows width (same as sibling stacks).

    Subclass ``VerticalGroup`` (``height: auto``), not ``Vertical`` (``1fr``):
    beside an auto-height heading, a ``1fr`` sibling often gets zero height.
    """

    def __init__(self, *terms: Node) -> None:
        """RDF nodes for each cell; new ``TermCard`` per layout rebuild."""
        self._cell_contents = list(terms)
        self._last_column_count = -1
        self._width_retries = 0
        super().__init__()

    def on_mount(self) -> None:
        self.call_after_refresh(self._rebuild_rows)

    def on_resize(self, _event: events.Resize) -> None:
        self._rebuild_rows()

    def _column_count_for_width(self, width: int) -> int:
        gutter = TERM_CARD_ROW_GAP
        cell = TERM_CARD_MIN_COLUMN_WIDTH
        return max(1, (width + gutter) // (cell + gutter))

    def _width_for_layout(self) -> int:
        """Inner width; fall back to parent when not laid out yet."""
        width = self.size.width
        if width > 0:
            return width
        parent = self.parent
        if parent is not None and parent.size.width > 0:
            return max(1, parent.size.width - 2)
        return 0

    def _rebuild_rows(self) -> None:
        if not self._cell_contents:
            self._last_column_count = -1
            self.remove_children()
            return

        width = self._width_for_layout()
        if width <= 0:
            if self._width_retries < TERM_CARD_ROWSTACK_WIDTH_RETRIES:
                self._width_retries += 1
                self.call_after_refresh(self._rebuild_rows)
            return

        self._width_retries = 0

        columns = self._column_count_for_width(width)
        if columns == self._last_column_count and self.displayed_children:
            return
        self._last_column_count = columns

        self.remove_children()
        row_start = 0
        total = len(self._cell_contents)
        while row_start < total:
            row_start = self._mount_row_starting_at(row_start, columns)

    def _mount_row_starting_at(self, row_start: int, columns: int) -> int:
        row_end = row_start + columns
        chunk = self._cell_contents[row_start:row_end]
        cells: list[TermCard | TermCardSlot] = [
            TermCard(term) for term in chunk
        ]
        while len(cells) < columns:
            cells.append(TermCardSlot(""))
        self.mount(TermCardRow(*cells))
        return row_end


class TermGroupSection(VerticalGroup):
    """One VANN group: optional heading plus a grid of term cards."""

    DEFAULT_CSS = """
    TermGroupSection {
        width: 1fr;
        height: auto;
        margin-bottom: 1;
    }
    TermGroupSection > Static {
        margin-bottom: 1;
    }
    """  # noqa: WPS115
