from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import Iterable

import funcy
from rdflib import URIRef
from rich.columns import Columns
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.models import NotLiteralNode


class TermStatus(StrEnum):
    STABLE = 'stable'
    ARCHAIC = 'archaic'
    TESTING = 'testing'
    UNSTABLE = 'unstable'


@dataclass
class TermAndStatus:
    term: URIRef
    status: TermStatus


class TermsContent(VerticalScroll):
    """Display grouped list of terms."""

    DEFAULT_CSS = """
    TermsContent {
        padding: 1;
    }
    """


class OntologyFacet(Facet[Widget]):
    """Render an ontology."""

    @cached_property
    def grouped_terms(self) -> dict[NotLiteralNode | None, list[TermAndStatus]]:
        """Group terms by VANN categories."""
        rows = self.stored_query('terms.sparql', iri=self.iri)
        grouped = [
            (
                row.get('group'),
                TermAndStatus(
                    term=row['term'],
                    status=status,
                ),
            )
            for row in rows
            if (
                status := TermStatus(
                    (status_literal := row.get('status'))
                    and status_literal.value
                    or 'stable',
                )
            ) != TermStatus.ARCHAIC
        ]

        return funcy.group_values(grouped)

    def show(self) -> Widget:
        """Render widget."""
        return Vertical(
            PageTitle(self.iri),
            TermsContent(
                Static(
                    Columns(
                        self._stream_columns(),
                        padding=(1, 2),
                    ),
                ),
            ),
        )

    def _stream_columns(self) -> Iterable[str]:
        for group, rows in self.grouped_terms.items():
            group_title = self.render(
                group,
                as_datatype=[URIRef('https://iolanta.tech/env/title')],
            ) if group is not None else '<Ungrouped>'

            rendered_terms = '\n'.join([
                self.render(
                    row.term,
                    as_datatype=[
                        URIRef('https://iolanta.tech/cli/link'),
                    ],
                )
                for row in rows
            ])

            yield f'[b]{group_title}[/b]\n\n{rendered_terms}'
