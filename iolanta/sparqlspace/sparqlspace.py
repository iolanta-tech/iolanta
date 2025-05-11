import functools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import rdflib
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Result


@dataclass
class SPARQLSpace:
    """SPARQL interface to the Web of Data."""

    graph: rdflib.Dataset = field(
        default_factory=functools.partial(
            rdflib.Dataset,
            default_union=True,
        ),
    )
    path: Annotated[
        Path | None,
        'Local directory to load into the graph.',
    ] = None

    def query(self, query: str | Query, **bindings) -> Result:
        """Execute a SPARQL query."""
        return self.graph.query(
            query_object=query,
            processor='sparqlspace',
            initBindings=bindings,
        )
