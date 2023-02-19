from typing import Iterable

import funcy
from rdflib import Literal

from iolanta.errors import InsufficientDataForRender
from iolanta.facet.rich import Renderable, RichFacet


class Link(RichFacet):
    def show(self) -> Renderable:
        if isinstance(self.iri, Literal):
            return self.iri.value

        rows = self.stored_query('link.sparql', node=self.iri)

        if not rows:
            raise InsufficientDataForRender(
                node=self.iri,
                iolanta=self.iolanta,
            )

        labels: Iterable[Literal] = funcy.pluck('label', rows)

        suitable_labels = [
            label
            for label in labels
            if label.language in {'en', None}
        ]

        return funcy.first(suitable_labels) or str(self.iri)
