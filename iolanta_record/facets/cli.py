import itertools

import funcy
from rdflib import BNode, Literal, URIRef
from rich.table import Table

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.cli.formatters.pretty import pretty_print_value
from iolanta.errors import InsufficientDataForRender
from iolanta.facet.rich import Renderable, RichFacet
from iolanta.namespaces import IOLANTA


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
        table.title = self.iolanta.render(
            self.iri,
            environments=[IOLANTA['cli-link']],
        )

        table.add_column(
            "Properties",
            no_wrap=True,
            justify="left",
            style="bold blue",
        )
        table.add_column("Values")

        for property_iri, property_values in dossier.items():
            try:
                table.add_row(
                    self.iolanta.render(
                        property_iri,
                        environments=[IOLANTA['cli-link']],
                    ),
                    ' - '.join(
                        str(
                            self.iolanta.render(
                                property_value,
                                environments=[IOLANTA['cli-link']],
                            ),
                        )
                        for property_value in property_values
                        if (
                            isinstance(property_value, URIRef)
                            or isinstance(property_value, BNode)
                            or (
                                isinstance(property_value, Literal)
                                and property_value.language in {None, 'en'}
                            )
                        )
                    ),
                )
            except InsufficientDataForRender as err:
                if err.is_hopeless:
                    continue

                raise

        return table
