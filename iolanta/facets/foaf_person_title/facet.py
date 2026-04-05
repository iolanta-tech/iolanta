from pathlib import Path

import funcy
from rdflib import URIRef

from iolanta import Facet
from iolanta.namespaces import DATATYPES


class FOAFPersonTitle(Facet[str]):
    """Show title for a foaf:Person object."""

    META = Path(__file__).parent / "title_foaf_person.yamlld"

    def show(self) -> str:
        """Render full name of a person."""
        row = funcy.first(
            self.stored_query(
                "names.sparql",
                person=self.this,
                language=self.iolanta.language,
            ),
        )

        if row is None:
            return self.render(
                self.this,
                as_datatype=URIRef("https://iolanta.tech/qname"),
            )

        family_name = row["family_name"]
        given_name = row["given_name"]

        return f"{given_name} {family_name}"
