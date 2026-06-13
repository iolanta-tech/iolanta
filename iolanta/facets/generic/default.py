from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Optional, cast

import funcy
from rdflib import Literal

from iolanta.facets.facet import Facet, FacetOutput


@dataclass
class Description:
    """A few properties of the object we use as row heading."""

    label: Optional[Literal] = None
    icon: Optional[Literal] = None
    url: Optional[Literal] = None
    comment: Optional[Literal] = None


class DefaultMixin(Facet[FacetOutput]):
    stored_queries_path = Path(__file__).parent / "sparql"

    @cached_property
    def description(self) -> Description:
        return Description(
            **funcy.first(
                self.stored_query("default.sparql", iri=self.this),
            ),
        )

    def show(self) -> FacetOutput:
        """Render the column."""
        if self.description.url:
            return self.render_link()

        return cast(FacetOutput, self.render_label())

    @abstractmethod
    def render_link(self) -> FacetOutput:
        """Render clickable link."""

    def render_label(self) -> str:
        label = self.description.label
        rendered_label = str(label.value) if label else self.render_fallback()

        if icon := self.description.icon:
            if self.as_datatype:
                rendered_icon = self.render(
                    icon,
                    as_datatype=self.as_datatype,
                )
            else:
                rendered_icon = icon.value
            rendered_label = f"{rendered_icon} {rendered_label}"

        return rendered_label

    def render_fallback(self) -> str:
        string_iri = str(self.this)

        if string_iri.startswith("local:"):
            string_iri = (
                string_iri.removeprefix(
                    "local:",
                )
                .replace(
                    "_",
                    " ",
                )
                .replace(
                    "-",
                    " ",
                )
                .capitalize()
            )

        return string_iri
