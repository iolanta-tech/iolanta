from rdflib import URIRef

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet, FacetOutput
from iolanta.models import ComputedQName, NotLiteralNode


class TextualLinkFacet(Facet[str]):
    def show(self) -> str:
        label = self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/env/title')]
        )

        return f'[@click="goto(\'{self.iri}\')"]{label}[/]'
