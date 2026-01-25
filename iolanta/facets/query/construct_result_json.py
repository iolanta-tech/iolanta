import json
from pathlib import Path
from typing import cast

from rdflib import Graph, Literal

from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import NotALiteral

META = Path(__file__).parent / 'data' / 'query_result.yamlld'


class ConstructResultJsonFacet(RichFacet):
    """Render CONSTRUCT query results as JSON."""

    META = META

    def show(self) -> Renderable:
        """Render Graph (CONSTRUCT result) as JSON."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)

        graph = cast(Graph, self.this.value)
        fieldnames = ('subject', 'predicate', 'object')
        return json.dumps(
            [
                dict(zip(fieldnames, triple))
                for triple in graph
            ],
            indent=2,
            default=str,
        )
