"""KGLint facet: deterministic KG linter with assertions and labels."""

import re
from pathlib import Path

import funcy
from rdflib import BNode, Literal, Node, URIRef

from iolanta import Facet
from iolanta.kglint.models import (
    Assertion,
    AssertionCode,
    LabelEntry,
    NodeBlank,
    NodeLiteral,
    NodeObject,
    NodeURI,
    Report,
    TripleRef,
)
from iolanta.namespaces import DATATYPES

QNAME_RE = re.compile(r'^\S+:\S+$')


def _serialize(node: Node) -> str:
    """Serialize node to stable string (N-Triples style)."""
    return node.n3()


def _looks_like_qname(label: str) -> bool:
    """True if label has the form prefix:localName (QName-shaped)."""
    return bool(QNAME_RE.match(label))


class KGLint(Facet[str]):
    """Deterministic Knowledge Graph linter: assertions + URI/blank labels."""

    META = Path(__file__).parent / 'kglint.yamlld'

    def _render_label(self, node: Node) -> str:
        """Human-readable label for a node (title facet)."""
        return str(self.render(node, as_datatype=DATATYPES.title))

    @funcy.cached_property
    @funcy.post_processing(list)
    def _triples(self):
        """All triples in the graph (cached)."""
        for row in self.stored_query('triples.sparql', graph=self.this):
            yield (row['subject'], row['predicate'], row['object'])

    @funcy.cached_property
    @funcy.post_processing(set)
    def _nodes(self):
        """URIRef and BNode terms that appear in triples (cached)."""
        for s, p, o in self._triples:
            for term in (s, p, o):
                if isinstance(term, (URIRef, BNode)):
                    yield term

    @funcy.cached_property
    @funcy.post_processing(dict)
    def label_by_node(self):
        """Rendered label per node (cached)."""
        for node in self._nodes:
            yield node, self._render_label(node)

    @funcy.cached_property
    @funcy.post_processing(funcy.group_values)
    def _triples_by_node(self):
        """Map each node to list of triples it participates in (cached)."""
        nodes = self._nodes
        for s, p, o in self._triples:
            for term in (s, p, o):
                if term in nodes:
                    yield term, (s, p, o)

    def _node_to_object(self, node: Node) -> NodeObject:
        """Convert RDF node to JSON node object (literal, uri, or blank)."""
        match node:
            case Literal():
                return NodeLiteral(
                    value=str(node),
                    datatype=str(node.datatype) if node.datatype else None,
                    language=node.language or None,
                )
            case URIRef():
                return NodeURI(value=str(node), label=self.label_by_node[node])
            case BNode():
                return NodeBlank(value=node.n3(), label=self.label_by_node[node])

    def _label_entries(self):
        """Yield label entries (node + triples) in deterministic order."""
        label_by_node = self.label_by_node
        triples_by_node = self._triples_by_node
        for node in sorted(self._nodes, key=_serialize):
            triples_refs = [
                TripleRef(
                    s=self._node_to_object(s),
                    p=self._node_to_object(p),
                    o=self._node_to_object(o),
                )
                for s, p, o in sorted(
                    triples_by_node[node],
                    key=lambda t: (_serialize(t[0]), _serialize(t[1]), _serialize(t[2])),
                )
            ]
            if isinstance(node, URIRef):
                entry_node = NodeURI(value=str(node), label=label_by_node[node])
            else:
                entry_node = NodeBlank(value=node.n3(), label=label_by_node[node])
            yield LabelEntry(node=entry_node, triples=triples_refs)

    def _assertions(self):
        """Yield all assertions (literal/uri/blank checks)."""
        label_by_node = self.label_by_node
        for s, p, o in self._triples:
            if isinstance(o, Literal):
                label = self._render_label(o)
                if label.startswith('http'):
                    yield Assertion(
                        severity='warning',
                        code=AssertionCode.LITERAL_LOOKS_LIKE_URI,
                        target=TripleRef(
                            s=self._node_to_object(s),
                            p=self._node_to_object(p),
                            o=self._node_to_object(o),
                        ),
                        message=(
                            'This RDF literal seems to be actually a URL. '
                            'Good chance is that it should not be a literal.'
                        ),
                    )
                elif _looks_like_qname(label):
                    yield Assertion(
                        severity='warning',
                        code=AssertionCode.LITERAL_LOOKS_LIKE_QNAME,
                        target=TripleRef(
                            s=self._node_to_object(s),
                            p=self._node_to_object(p),
                            o=self._node_to_object(o),
                        ),
                        message=(
                            'This RDF literal seems to be actually a QName '
                            '(prefixed URI). Good chance is that it should '
                            'not be a literal.'
                        ),
                    )
        for node in self._nodes:
            label = label_by_node[node]
            if isinstance(node, URIRef):
                if str(node) == label:
                    yield Assertion(
                        severity='error',
                        code=AssertionCode.URI_LABEL_IDENTICAL,
                        target=NodeURI(value=str(node), label=label),
                        message=(
                            'For this URI, the label is the same as the URI. '
                            'We were unable to render that URI.'
                        ),
                    )
            elif isinstance(node, BNode):
                if str(node) == label:
                    yield Assertion(
                        severity='warning',
                        code=AssertionCode.BLANK_LABEL_IDENTICAL,
                        target=NodeBlank(value=node.n3(), label=label),
                        message=(
                            'For this blank node, the label is the same as '
                            'the blank node. We were unable to render that '
                            'blank node.'
                        ),
                    )

    def show(self) -> str:
        """Build report (assertions + labels) and return JSON string."""
        labels_list = list(self._label_entries())
        assertions_list = sorted(
            self._assertions(),
            key=lambda a: (a.severity, a.code, a.target.model_dump_json()),
        )
        report = Report(assertions=assertions_list, labels=labels_list)
        return report.model_dump_json(indent=2, exclude_none=True)
