from textual.containers import ScrollableContainer

from iolanta.facets.textual_browser.models import FlipOption
from iolanta.models import NotLiteralNode


class Page(ScrollableContainer):
    """Page in Iolanta browser."""

    def __init__(
        self,
        renderable,
        iri: NotLiteralNode,
        page_id: str,
        flip_options: list[FlipOption],
    ):
        """Initialize the page and set bindings."""
        super().__init__(renderable, id=page_id)
        for number, flip_option in enumerate(flip_options, start=1):
            self._bindings.bind(
                keys=str(number),
                description=flip_option.title,
                action=(
                    f"app.goto('{iri}', '{flip_option.facet_iri}')"
                ),
            )
