from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet
from iolanta.models import NotLiteralNode, ComputedQName


class QNameFacet(Facet[str]):
    def show(self) -> str:
        qname: ComputedQName | NotLiteralNode = node_to_qname(
            self.iri,
            self.iolanta.graph,
        )

        if isinstance(qname, ComputedQName):
            return f'{qname.namespace_name}:{qname.term}'

        return str(self.iri)
