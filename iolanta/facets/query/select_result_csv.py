import csv
import io
from pathlib import Path

from rdflib import Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class SelectResultCsvFacet(RichFacet):
    """Render SELECT query results as CSV."""

    META = META

    def show(self) -> Renderable:
        """Render SelectResult as CSV."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        query_result = self.this.value

        if not query_result:
            return ""

        output = io.StringIO()
        first_row = query_result[0]
        fieldnames = first_row.keys()

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(query_result)

        return output.getvalue()
