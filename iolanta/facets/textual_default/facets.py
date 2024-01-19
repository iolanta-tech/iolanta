from pathlib import Path

import funcy
from rdflib import URIRef
from rich.markdown import Markdown
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, Static

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet
from iolanta.namespaces import IOLANTA


class TextualDefaultFacet(Facet[Widget]):
    """Default rendering engine."""

    def show(self) -> Widget:
        rows = self.stored_query('label.sparql', iri=self.iri)
        first_row = funcy.first(rows)

        comment = None
        if first_row:
            label = first_row['label']
            comment = first_row.get('comment')
        else:
            qname = node_to_qname(self.iri, self.iolanta.graph)
            label = f'{qname.namespace_name}:{qname.term}'

        types = funcy.pluck(
            'type',
            self.stored_query('types.sparql', iri=self.iri),
        )

        text_path = Path(__file__).parent / 'templates/default.md'
        text = text_path.read_text().format(
            label=label,
            comment=comment or '',
        )

        formatted_types = ' · '.join(
            self.render(
                rdf_type,
                [URIRef('https://iolanta.tech/cli/link')],
            )
            for rdf_type in types
        ) or '[em](unknown)[/]'

        return Vertical(
            Label(Markdown(text)),
            Static(f'\n  [bold]∈ Types:[/] {formatted_types}')
        )
