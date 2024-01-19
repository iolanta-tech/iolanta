from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet, FacetOutput
from iolanta.models import ComputedQName


class TextualLinkFacet(Facet[str]):
    def show(self) -> str:
        rows = self.stored_query('link.sparql', iri=self.iri)

        try:
            label = rows[0]['label']
        except IndexError:
            qname: ComputedQName = node_to_qname(self.iri, graph=self.iolanta.graph)
            label = f'{qname.namespace_name}:{qname.term}'

        return f'[@click="goto(\'{self.iri}\')"]{label}[/]'
