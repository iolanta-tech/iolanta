from dominate.tags import a, span
from dominate.util import raw

from iolanta.facets.generic.default import DefaultMixin
from iolanta.facets.html.base import HTMLFacet


class Default(DefaultMixin, HTMLFacet):
    """Default renderer."""

    def render_link(self):
        return a(
            self.render_label(),
            href=self.description.url,
            title=self.description.comment,
        )

    def render_label(self):
        label = super().render_label()

        if comment := self.description.comment:
            return span(
                raw(label),
                title=comment,
            )

        return label
