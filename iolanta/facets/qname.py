from iolanta.facets.facet import Facet
from iolanta.models import ComputedQName, NotLiteralNode
from iolanta.node_to_qname import node_to_qname


class QNameFacet(Facet[str]):
    """Render an IRI as a QName."""

    def show(self) -> str:
        """Return a qname."""
        qname: ComputedQName | NotLiteralNode = node_to_qname(
            self.iri,
            self.iolanta.graph,
        )

        if isinstance(qname, ComputedQName):
            return f'{qname.namespace_name}:{qname.term}'

        return str(self.iri)
