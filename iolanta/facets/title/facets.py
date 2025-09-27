import funcy
from rdflib import URIRef

from iolanta.facets.facet import Facet

PRIORITIES = [   # noqa: WPS407
    'dc_title',
    'schema_title',
    'schema_name',
    'rdfs_label',
    'foaf_name',
    'literal_form',
    'preferred_label',
]


class TitleFacet(Facet[str]):
    """Title of an object."""

    def show(self) -> str:
        """Render title of a thing."""
        choices = self.stored_query(
            'title.sparql',
            iri=self.this,
            language=self.iolanta.language,
        )

        if choices:
            row = funcy.first(choices)
            for alternative in PRIORITIES:
                if label := row.get(alternative):
                    return str(label)

        return str(self.this)
