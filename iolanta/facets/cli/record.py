from dataclasses import field, dataclass

from rdflib import URIRef, OWL
from rich.table import Table

from iolanta.facets.cli import RichFacet, Renderable
from iolanta.facets.facet import FacetOutput
from iolanta.namespaces import IOLANTA


@dataclass
class Record(RichFacet):
    skipped_properties: set[URIRef] = field(default_factory=lambda: {
        OWL.sameAs,
    })

    def show(self) -> Renderable:
        rows = self.stored_query('record.sparql', node=self.iri)

        caption = self.render(self.iri, environments=[IOLANTA['cli/record/title']])

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
                environments=[IOLANTA['cli/record/property']],
            )
            rendered_value = self.render(
                row['value'],
                environments=[IOLANTA['cli/record/value']],
            )
            table.add_row(rendered_property, rendered_value)

        return table
