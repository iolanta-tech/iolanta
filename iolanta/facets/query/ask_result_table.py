from pathlib import Path

from rdflib import Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class AskResultTableFacet(RichFacet):
    """Render ASK query results as table/text."""

    META = META

    def show(self) -> Renderable:
        """Render bool (ASK result) as text."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        query_result = self.this.value

        return "✅ `True`" if query_result else "❌ `False`"
