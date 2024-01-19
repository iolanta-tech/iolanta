from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet, FacetOutput
from iolanta.models import ComputedQName, NotLiteralNode


class TextualLinkFacet(Facet[str]):
    def show(self) -> str:
        rows = self.stored_query('link.sparql', iri=self.iri)

        try:
            label = rows[0]['label']
        except IndexError:
            qname: ComputedQName | NotLiteralNode = node_to_qname(self.iri, graph=self.iolanta.graph)

            if isinstance(qname, ComputedQName):
                label = f'{qname.namespace_name}:{qname.term}'
            else:
                label = str(qname)

        return f'[@click="goto(\'{self.iri}\')"]{label}[/]'
