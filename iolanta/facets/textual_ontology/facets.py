from rich.columns import Columns

from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import Iterable

import funcy
from rdflib import URIRef, Literal
from textual.widget import Widget
from textual.widgets import Label, Static, ListView, ListItem

from iolanta.facets.facet import Facet
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


class TermsContent(Static):
    DEFAULT_CSS = '''
    TermsContent {
        padding: 1;
    }
    '''


class OntologyFacet(Facet[Widget]):
    @cached_property
    def grouped_terms(self) -> dict[NotLiteralNode | None, list[TermAndStatus]]:
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
            if (status := TermStatus(
                (status_literal := row.get('status'))
                and status_literal.value
                or 'stable'
            )) != TermStatus.ARCHAIC
        ]

        return funcy.group_values(grouped)

    def _stream_columns(self) -> Iterable[str]:
        for group, rows in self.grouped_terms.items():
            group_title = self.render(
                group,
                environments=[URIRef('https://iolanta.tech/env/title')],
            ) if group is not None else '<Ungrouped>'

            content = '\n'.join([
                self.render(
                    row.term,
                    environments=[
                        URIRef('https://iolanta.tech/cli/link'),
                    ],
                )
                for row in rows
            ])

            column = f'[b]{group_title}[/b]\n\n' + content

            yield column

    def show(self) -> Widget:
        return TermsContent(Columns(self._stream_columns(), padding=(1, 2)))
