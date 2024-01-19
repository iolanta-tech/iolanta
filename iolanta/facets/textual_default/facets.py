import logging
from pathlib import Path

import funcy
from rdflib import URIRef
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, Static, DataTable

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet
from iolanta.models import ComputedQName, NotLiteralNode
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
            qname: ComputedQName | NotLiteralNode = node_to_qname(self.iri, self.iolanta.graph)
            if isinstance(qname, ComputedQName):
                label = f'{qname.namespace_name}:{qname.term}'
            else:
                label = str(qname)

        text_path = Path(__file__).parent / 'templates/default.md'
        text = text_path.read_text().format(
            label=label,
            comment=comment or '',
        )

        property_rows = self.stored_query(
            'properties.sparql',
            iri=self.iri,
        )

        property_pairs = [
            (row['property'], row['object'])
            for row in property_rows
        ]

        children = [Label(Markdown(text))]

        instances = list(funcy.pluck(
            'instance',
            self.stored_query('instances.sparql', iri=self.iri),
        ))
        if instances:
            children.append(Label('\n[bold]A few instances of this class[/]\n'))
            children.append(Label(
                ' · '.join(
                    self.render(
                        instance,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    )
                    for instance in instances
                ),
            ))

        grouped_properties = funcy.group_values(property_pairs)
        if grouped_properties:
            properties_table = DataTable(show_header=True, show_cursor=False)
            properties_table.add_columns('Property', 'Value')
            properties_table.add_rows([
                (
                    self.render(
                        property_iri,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    ),
                    ' · '.join(
                        self.render(
                            property_value,
                            environments=[URIRef('https://iolanta.tech/cli/link')]
                        )
                        for property_value in property_values
                    ),
                )
                for property_iri, property_values in grouped_properties.items()
            ])

            children.append(Label('\n[bold]Properties[/]\n'))
            children.append(properties_table)

        return Vertical(*children)
