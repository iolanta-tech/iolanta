from rdflib import URIRef

from iolanta.facets.facet import Facet


PRIORITIES = [
    'dc_title',
    'schema_title',
    'rdfs_label',
    'foaf_name',
]


class TitleFacet(Facet[str]):
    """Title of an object."""

    def show(self) -> str:
        choices = self.stored_query('title.sparql', iri=self.iri)

        try:
            [row] = choices
        except ValueError:
            raise ValueError(
                f'Not exactly one choice, what do we do?! {choices}',
            )

        for alternative in PRIORITIES:
            if label := row.get(alternative):
                return str(label)

        return self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/qname')],
        )
