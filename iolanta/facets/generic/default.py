from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional, TypedDict

import funcy
from rdflib import Literal

from iolanta.facets.facet import Facet, FacetOutput


@dataclass
class Description:
    """A few properties of the object we use as row heading."""

    label: Optional[Literal] = None
    symbol: Optional[Literal] = None
    url: Optional[Literal] = None
    comment: Optional[Literal] = None


class DefaultMixin(Facet[FacetOutput]):
    stored_queries_path = Path(__file__).parent / 'sparql'

    @cached_property
    def description(self) -> Description:
        return Description(
            **funcy.first(
                self.stored_query('default.sparql', iri=self.iri),
            ),
        )

    def show(self) -> FacetOutput:
        """Render the column."""
        if self.description.url:
            return self.render_link()

        return self.render_label()

    @abstractmethod
    def render_link(self) -> FacetOutput:
        """Render clickable link."""

    def render_label(self) -> str:
        if not (label := self.description.label):
            label = self.render_fallback()

        if isinstance(label, Literal):
            label = label.value

        if symbol := self.description.symbol:
            rendered_symbol = self.render(
                symbol,
                environments=[self.environment],
            )
            label = f'{rendered_symbol} {label}'

        return label

    def render_fallback(self) -> str:
        string_iri = str(self.iri)

        if string_iri.startswith('local:'):
            string_iri = string_iri.removeprefix(
                'local:',
            ).replace(
                '_', ' ',
            ).replace(
                '-', ' ',
            ).capitalize()

        return string_iri
