import funcy
from rdflib import URIRef, Graph
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label, Static, Button

from iolanta.facets.facet import Facet, FacetOutput


class OntologyTerms(Widget):
    DEFAULT_CSS = """
    OntologyTerms {
        layout: grid;
        grid-size: 3;
        grid-rows: 3;
    }
    
    .box {
        width: 100%;
        # border: none;
        # background: none;
    }
    """


class OntologyFacet(Facet[Widget]):
    def show(self) -> Widget:
        terms = funcy.lpluck(
            'term',
            self.stored_query('terms.sparql', iri=self.iri),
        )

        # g: Graph = self.iolanta.graph
        # raise ValueError([k for k, v in g.namespaces()])

        return OntologyTerms(*[
            Button(
                self.render(
                    term,
                    environments=[URIRef('https://iolanta.tech/env/title')],
                ),
                classes='box',
            )
            for term in terms
        ])
