import json
from pathlib import Path

from rdflib import Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class AskResultJsonFacet(RichFacet):
    """Render ASK query results as JSON."""

    META = META

    def show(self) -> Renderable:
        """Render bool (ASK result) as JSON."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        query_result = self.this.value

        return json.dumps(query_result)
