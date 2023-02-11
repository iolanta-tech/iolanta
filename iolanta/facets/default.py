from pathlib import Path
from typing import Optional, TypedDict

import funcy
from dominate.tags import a, span  # noqa: WPS347
from rdflib import Literal

from iolanta.facet import Facet


class DefaultRow(TypedDict):
    """A few properties of the object we use as row heading."""

    label: Optional[Literal]
    symbol: Optional[Literal]
    url: Optional[Literal]
    comment: Optional[Literal]


class Default(Facet):
    """Default renderer."""

    def show(self):
        """Render the column."""
        row: DefaultRow = funcy.first(
            self.query(
                (
                    Path(__file__).parent / 'sparql/default.sparql'
                ).read_text(),
                iri=self.iri,
            ),
        )

        if row.get('url'):
            return self._render_link(row)

        return self._render_label(row)

    def _render_link(self, row: DefaultRow):
        comment = row.get('comment')
        return a(
            self._render_label({   # type: ignore
                row_key: row_value
                for row_key, row_value in row.items()
                if row_key != 'comment'
            }),
            href=row['url'],
            title=comment,
        )

    def _render_label(self, row: DefaultRow):
        label = row.get('label')

        if label is None:
            label = self._render_fallback()

        if symbol := row.get('symbol'):
            label = f'{symbol} {label}'

        if comment := row.get('comment'):
            return span(
                label,
                title=comment,
            )

        return label

    def _render_fallback(self) -> str:
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
