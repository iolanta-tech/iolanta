from rdflib import Literal, URIRef
from rich.style import Style
from rich.text import Text

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet, FacetOutput
from iolanta.models import ComputedQName, NotLiteralNode


class TextualLinkFacet(Facet[str]):
    def show(self) -> str | Text:
        if isinstance(self.iri, Literal):
            return Text(self.iri, style=Style(color='grey37'))

        label = self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/env/title')],
        )

        return f'[@click="app.goto(\'{self.iri}\')"]{label}[/]'
