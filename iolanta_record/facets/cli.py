import itertools

import funcy
from rich.table import Table

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.cli.formatters.pretty import pretty_print_value
from iolanta.facet.rich import RichFacet, Renderable


class CLI(RichFacet):
    def show(self) -> Renderable:
        rows = self.query(
            '''
            SELECT ?property ?value WHERE {
                $iri ?property ?value .
            } ORDER BY ?property ?value
            ''',
            iri=self.iri,
        )

        pairs = [
            (row['property'], row['value'])
            for row in rows
        ]

        dossier = {
            property_iri: list(
                map(
                    funcy.last,
                    property_values,
                ),
            )
            for property_iri, property_values
            in itertools.groupby(
                pairs,
                key=funcy.first,
            )
        }

        table = Table.grid(padding=1, pad_edge=True)
        table.title = str(self.iri)
        table.add_column(
            "Properties",
            no_wrap=True,
            justify="left",
            style="bold blue",
        )
        table.add_column("Values")

        for property_iri, property_values in dossier.items():
            table.add_row(
                # FIXME:
                #   title: Render property instead of pretty-printing raw IRI
                #   is-blocked-by: record-render-strategy
                pretty_print_value(
                    node_to_qname(
                        property_iri,
                        self.iolanta.graph,
                    ),
                ),
                '\n'.join(
                    map(
                        str,
                        # FIXME:
                        #   title: Render property values instead of prettyprint
                        #   is-blocked-by: record-render-strategy
                        property_values,
                    ),
                )
            )

        return table
