from typing import Iterable

from textual.containers import Horizontal

from iolanta.facets.textual_nanopublication.term_widget import TermWidget
from iolanta.widgets.mixin import IolantaWidgetMixin


class TermList(IolantaWidgetMixin, Horizontal):
    """Display a sequence of terms."""

    DEFAULT_CSS = """
    TermList {
        padding: 1 2;
        height: auto;
    }
    """

    def __init__(self, terms: Iterable[TermWidget]):
        """Initialize."""
        self.terms = terms
        super().__init__()

    def compose(self):
        """Fill in the term stubs."""
        yield from self.terms

    def on_mount(self):
        """Initialize terms rendering."""
        self.run_worker(self.render_terms, thread=True)

    def render_terms(self):
        """Render terms."""
        child: TermWidget
        for child in self.children:
            child.renderable = self.iolanta.render(
                child.uri,
                as_datatype=child.as_datatype,
            )
