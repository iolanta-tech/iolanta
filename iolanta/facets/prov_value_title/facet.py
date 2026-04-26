from pathlib import Path

import funcy
from rdflib import URIRef

from iolanta import Facet
from iolanta.namespaces import DATATYPES


class ProvValueTitle(Facet[str]):
    """Title for provenance-qualified values."""

    META = Path(__file__).parent / "prov_value_title.yamlld"

    def show(self) -> str:
        """Render a value with its source."""
        row = funcy.first(
            self.stored_query(
                "title.sparql",
                node=self.this,
                language=self.language,
            ),
        )

        if row is None:
            return str(
                self.render(
                    self.this,
                    as_datatype=URIRef("https://iolanta.tech/qname"),
                ),
            )

        value_title = self.render(row["value"], as_datatype=DATATYPES.title)
        source_title = self.render(row["source"], as_datatype=DATATYPES.title)
        return f"{value_title} ⇐ {source_title}"
