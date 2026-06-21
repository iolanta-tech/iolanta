from pathlib import Path
from typing import Iterable

from rdflib import BNode, Literal, URIRef
from rdflib.term import IdentifiedNode, Node

from iolanta.mermaid.facet import Mermaid
from iolanta.mermaid.models import (
    Diagram,
    MermaidScalar,
    MermaidSubgraph,
    raw_literal_title,
)
from iolanta.mermaid.raw_rdf.models import (
    MermaidRawBlankNode,
    MermaidRawEdge,
    MermaidRawLiteral,
    MermaidRawURINode,
)
from iolanta.models import NotLiteralNode


def _raw_mermaid_node_identity(
    node: MermaidRawURINode | MermaidRawLiteral | MermaidRawBlankNode,
) -> IdentifiedNode | Literal:
    """RDF term used to dedupe raw Mermaid node declarations."""
    match node:
        case MermaidRawURINode(uri=uri):
            return uri
        case MermaidRawLiteral(literal=literal):
            return literal
        case MermaidRawBlankNode(node=bnode):
            return bnode


def filter_raw_nodes(
    edges: Iterable[MermaidRawEdge],
    except_uris: Iterable[NotLiteralNode],
) -> Iterable[MermaidRawURINode | MermaidRawLiteral | MermaidRawBlankNode]:
    """Yield one raw Mermaid node declaration per RDF graph node."""
    nodes = [node for edge in edges for node in edge.nodes]
    literals_in_edges = {
        edge.target for edge in edges if isinstance(edge.target, MermaidRawLiteral)
    }
    seen: set[IdentifiedNode | Literal] = set()
    for node in nodes:
        if isinstance(node, MermaidRawLiteral) and node not in literals_in_edges:
            continue

        if isinstance(node, MermaidRawURINode) and node.uri in except_uris:
            continue

        if isinstance(node, MermaidRawBlankNode) and node.node in except_uris:
            continue

        if isinstance(node, MermaidSubgraph):
            continue

        identity = _raw_mermaid_node_identity(node)
        if identity in seen:
            continue
        seen.add(identity)
        yield node


class RawRDFMermaid(Mermaid):
    """Mermaid diagram for exact RDF graph triples."""

    META = Path(__file__).parent / "raw_rdf_mermaid.yamlld"

    @property
    def stored_queries_path(self) -> Path:
        """Use the generic Mermaid graph query."""
        return Path(__file__).parents[1] / "sparql"

    def mermaid_title(self, node: Node) -> str:
        """Render Mermaid label text from graph terms without Turtle syntax."""
        if isinstance(node, Literal):
            return raw_literal_title(node)

        return str(node)

    def as_mermaid(self, node: Node):
        """Convert RDF terms to raw Mermaid nodes."""
        match node:
            case URIRef() as uri:
                if uri in self.subgraph_uris:
                    return MermaidSubgraph(
                        children=[],
                        uri=uri,
                        title=self.mermaid_title(uri),
                    )

                return MermaidRawURINode(
                    uri=uri,
                    title=self.mermaid_title(uri),
                )
            case Literal() as literal:
                return MermaidRawLiteral(literal=literal)
            case BNode() as bnode:
                return MermaidRawBlankNode(
                    node=bnode,
                    title=self.mermaid_title(bnode),
                )
            case unknown:
                unknown_type = type(unknown)
                raise ValueError(f"Unknown something: {unknown} ({unknown_type})")

    def construct_mermaid_for_graph(self, graph: URIRef) -> Iterable[MermaidScalar]:
        """Render every triple in a graph as raw RDF Mermaid."""
        rows = self.stored_query("graph.sparql", this=graph)
        edges = [
            MermaidRawEdge(
                source=self.as_mermaid(row["s"]),
                target=self.as_mermaid(row["o"]),
                title=self.mermaid_title(row["p"]),
                predicate=row["p"],
            )
            for row in rows
        ]
        nodes = list(
            filter_raw_nodes(
                edges=edges,
                except_uris=self.subgraph_uris,
            ),
        )

        return *nodes, *edges

    def show(self) -> str:
        """Render raw RDF Mermaid diagram."""
        if not isinstance(self.this, URIRef):
            raise ValueError(f"Expected URIRef graph, got: {self.this}")

        direct_children = self.construct_mermaid_for_graph(self.this)
        subgraphs = self.construct_mermaid_subgraphs()
        return str(Diagram(children=[*direct_children, *subgraphs]))
