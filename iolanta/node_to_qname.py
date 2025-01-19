import logging

from classes import typeclass
from rdflib import Graph, URIRef
from rdflib.term import Node

from iolanta.models import ComputedQName

logger = logging.getLogger(__name__)


@typeclass
def node_to_qname(node: Node, graph: Graph):
    """Convert a node to a QName."""


@node_to_qname.instance(object)
def _object_to_qname(node: URIRef, graph: Graph):
    return node


@node_to_qname.instance(URIRef)
def _uriref_to_qname(node: URIRef, graph: Graph):
    try:
        qname = ComputedQName(*graph.compute_qname(node))   # type: ignore

    except ValueError:
        return node

    except NameError as err:
        logger.exception(f'NameError! On: {node} Error: {err}')
        return node

    if qname.namespace_name.startswith('ns'):
        return node

    return qname
