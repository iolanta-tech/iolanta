from pathlib import Path

from rdflib import Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class AskResultCsvFacet(RichFacet):
    """Render ASK query results as CSV."""

    META = META

    def show(self) -> Renderable:
        """Render bool (ASK result) as CSV."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        query_result = self.this.value

        return "result\n" + str(query_result).lower()
