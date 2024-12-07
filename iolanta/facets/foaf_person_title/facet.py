import funcy

from iolanta import Facet
from iolanta.namespaces import DATATYPES


class FOAFPersonTitle(Facet[str]):
    """Show title for a foaf:Person object."""

    def show(self) -> str:
        """Render full name of a person."""
        row = funcy.first(self.stored_query('names.sparql', person=self.iri))

        if row is None:
            # Render default title.
            return self.render(
                self.iri,
                as_datatype=DATATYPES['fallback-title'],
            )

        family_name = row['family_name']
        given_name = row['given_name']

        return f'{given_name} {family_name}'
