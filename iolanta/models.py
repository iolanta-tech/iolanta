import re
from enum import Enum
from typing import Any, Dict, List, NamedTuple, Union

from rdflib import Literal, URIRef
from rdflib.term import BNode, Node, Variable


class ComputedQName(NamedTuple):
    """QName computed from an URIRef."""

    namespace_name: str
    namespace_url: str
    term: str


class QueryResultsFormat(str, Enum):
    """Format to print query results in CLI."""

    PRETTY = 'pretty'
    CSV = 'csv'
    JSON = 'json'


# JSON-LD context
LDContext = Union[Dict[str, Any], List[Dict[str, Any]]]   # type: ignore
LDDocument = Union[Dict[str, Any], List[Dict[str, Any]]]  # type: ignore

NotLiteralNode = Union[URIRef, BNode]

# Named context URLs
ContextAliases = Dict[str, str]


def render_node(node: Node) -> str:
    """Render an RDFLib node as string."""
    if isinstance(node, URIRef):
        return f'<{node}>'

    if isinstance(node, Literal):
        rendered_node = f'"{node}"'
        if node.datatype:
            rendered_node = f'{rendered_node}^^{node.datatype}'

        if node.language:
            rendered_node = f'{rendered_node}@{node.language}'

        return rendered_node

    return f'<??? What is this? {node} ???>'


class Triple(NamedTuple):
    """RDF triple."""

    subject: NotLiteralNode
    predicate: NotLiteralNode
    object: URIRef | Literal  # noqa: WPS125

    def as_quad(self, graph: URIRef) -> 'Quad':
        """Add graph to this triple and hence get a quad."""
        return Quad(
            subject=self.subject,
            predicate=self.predicate,
            object=self.object,
            graph=graph,
        )


class TripleWithVariables(NamedTuple):
    """RDF triple."""

    subject: NotLiteralNode | Variable
    predicate: NotLiteralNode | Variable
    object: Node | Variable



class TripleTemplate(NamedTuple):
    subject: NotLiteralNode | None
    predicate: NotLiteralNode | None
    object: Node | None


def _normalize_term(term: Node):
    if isinstance(term, URIRef) and term.startswith('http://'):
        return URIRef(re.sub('^http', 'https', term))

    return term


class Quad(NamedTuple):
    """Triple assigned to a named graph."""

    subject: Node
    predicate: Node
    object: Node  # noqa: WPS125
    graph: URIRef

    def as_triple(self):
        """Convert this to triple."""
        return Triple(self.subject, self.predicate, self.object)

    def __repr__(self):
        """Represent the quad as string."""
        rendered_subject = render_node(self.subject)
        rendered_predicate = render_node(self.predicate)
        rendered_object = render_node(self.object)
        rendered_graph = render_node(self.graph)

        return (
            f'({rendered_subject} {rendered_predicate} {rendered_object} @ '
            f'{rendered_graph})'  # noqa: WPS326
        )

    def replace(self, mapping: dict[Node, URIRef]):
        """Replace variables in the quad."""
        terms = [
            mapping.get(term, term)
            for term in self
        ]

        return Quad(*terms)

    def normalize(self) -> 'Quad':
        """Normalize the quad by applying normalization to all its terms."""
        terms = [
            _normalize_term(term)
            for term in self
        ]
        return Quad(*terms)
