from functools import cached_property
from typing import Iterable

import funcy
from rdflib import URIRef
from textual.widget import Widget
from textual.widgets import Label, Static, ListView, ListItem

from iolanta.facets.facet import Facet
from iolanta.models import NotLiteralNode


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
    def grouped_terms(self) -> dict[NotLiteralNode | None, list[NotLiteralNode]]:
        rows = self.stored_query('terms.sparql', iri=self.iri)
        groups_and_terms = [
            (row.get('group'), row['term'])
            for row in rows
        ]

        return funcy.group_values(groups_and_terms)

    def _stream_group_widgets(self) -> Iterable[Widget]:
        for group, terms in self.grouped_terms.items():
            group_title = self.render(
                group,
                environments=[URIRef('https://iolanta.tech/env/title')],
            ) if group is not None else '<Ungrouped>'

            list_items = [
                ListItem(
                    Static(
                        self.render(
                            term,
                            environments=[URIRef('https://iolanta.tech/env/title')],
                        ),
                    ),
                    id=term,
                ) for term in terms
            ]

            list_view = ListView(*list_items)

            yield Group(
                Label(f'[bold]{group_title}[/bold]\n'),
                list_view,
            )

    def show(self) -> Widget:
        return Terms(*self._stream_group_widgets())
