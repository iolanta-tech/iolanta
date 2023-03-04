from rich.style import Style
from rich.text import Text

from iolanta.facets.cli import Renderable, RichFacet
from iolanta.facets.generic.default import DefaultMixin


class Default(DefaultMixin, RichFacet):
    def render_link(self) -> Renderable:
        return Text(
            self.render_label(),
            style=Style(link=self.description.url),
        )
