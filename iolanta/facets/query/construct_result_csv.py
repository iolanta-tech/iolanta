import csv
import io
from pathlib import Path
from typing import cast

from rdflib import Graph, Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class ConstructResultCsvFacet(RichFacet):
    """Render CONSTRUCT query results as CSV."""

    META = META

    def show(self) -> Renderable:
        """Render Graph (CONSTRUCT result) as CSV."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        graph = cast(Graph, self.this.value)

        if not graph:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(('subject', 'predicate', 'object'))
        writer.writerows(graph)

        return output.getvalue()
