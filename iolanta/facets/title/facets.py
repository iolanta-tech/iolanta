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
]


class TitleFacet(Facet[str]):
    """Title of an object."""

    def show(self) -> str:
        """Render title of a thing."""
        choices = self.stored_query(
            'title.sparql',
            iri=self.iri,
            language=self.iolanta.language,
        )

        if choices:
            row = funcy.first(choices)
            for alternative in PRIORITIES:
                if label := row.get(alternative):
                    return str(label)

        return self.render(
            self.iri,
            as_datatype=URIRef('https://iolanta.tech/qname'),
        )
