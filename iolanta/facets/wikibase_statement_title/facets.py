import funcy
from rdflib import URIRef

from iolanta.facets.facet import Facet
from iolanta.namespaces import DATATYPES


class WikibaseStatementTitle(Facet[str]):
    """Calculate title for a Wikibase Statement."""

    def show(self) -> str:
        """Render the title."""
        rows = self.stored_query(
            'statement-title.sparql',
            statement=self.iri,
            language=self.language,
        )

        row = funcy.first(rows)
        if not row:
            return self.render(
                self.iri,
                as_datatype=URIRef('https://iolanta.tech/qname'),
            )

        return self.render(
            row['entity'],
            as_datatype=DATATYPES.title,
        )
