from functools import cached_property

import funcy
from rdflib import BNode, URIRef
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView

from iolanta.facets.facet import Facet
from iolanta.facets.textual_default.facets import TripleURIRef
from iolanta.models import NotLiteralNode


class TextualProvenanceFacet(Facet[Widget]):
    def show(self) -> Widget:
        uri = TripleURIRef(self.iri)
        triple = uri.as_triple()

        instances = funcy.lpluck(
            'graph',
            self.stored_query(
                'graphs.sparql',
                subject=triple.subject,
                predicate=triple.predicate,
                object=triple.object,
            ),
        )

        raise ValueError(instances)
