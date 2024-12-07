from dataclasses import dataclass, field

from rdflib import URIRef
from rich.table import Table

from iolanta.facets.cli import Renderable, RichFacet
from iolanta.namespaces import IOLANTA, OWL


@dataclass
class Record(RichFacet):
    skipped_properties: set[URIRef] = field(
        default_factory=lambda: {
            OWL.sameAs,
        },
    )

    def show(self) -> Renderable:
        return "RECORD"
        rows = self.stored_query('record.sparql', node=self.iri)

        caption = self.render(self.iri, as_datatype=IOLANTA['cli/title'])

        table = Table(
            show_header=False,
            title=caption,
        )

        rows = [
            row for row in rows
            if row['property'] not in self.skipped_properties
        ]

        if not rows:
            return caption

        for row in rows:
            rendered_property = self.render(
                row['property'],
                as_datatype=IOLANTA['cli/record/property'],
            )
            rendered_value = self.render(
                row['value'],
                as_datatype=IOLANTA['cli/record/value'],
            )
            table.add_row(rendered_property, rendered_value)

        return table
