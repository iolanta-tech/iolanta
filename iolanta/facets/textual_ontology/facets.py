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


class Terms(Widget):
    DEFAULT_CSS = """
    Terms {
        layout: grid;
        grid-size: 3;
    }
    """

    def on_list_view_selected(self, event: ListView.Selected):
        self.app.action_goto(event.item.id)


class Group(Widget):
    DEFAULT_CSS = """
    Group {
        margin: 1;
    }
    """


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

    def _stream_group_widgets(self) -> Iterable[Widget]:
        for group, rows in self.grouped_terms.items():
            group_title = self.render(
                group,
                environments=[URIRef('https://iolanta.tech/env/title')],
            ) if group is not None else '<Ungrouped>'

            list_items = [
                ListItem(
                    Static(
                        self.render(
                            row.term,
                            environments=[
                                URIRef('https://iolanta.tech/env/title'),
                            ],
                        ),
                    ),
                    id=row.term,
                )
                for row in rows
            ]

            list_view = ListView(*list_items)

            yield Group(
                Label(f'[bold]{group_title}[/bold]\n'),
                list_view,
            )

    def show(self) -> Widget:
        return Terms(*self._stream_group_widgets())
