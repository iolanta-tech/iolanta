import functools
from pathlib import Path
from typing import Iterable

import boltons
import cachetools
import funcy
from boltons.cacheutils import cached, cachedmethod
from pydantic import AnyUrl
from rdflib import BNode, Literal, Node, URIRef

from iolanta import Facet
from iolanta.mermaid.models import (
    Diagram,
    MermaidBlankNode,
    MermaidEdge,
    MermaidLiteral,
    MermaidScalar,
    MermaidSubgraph,
    MermaidURINode,
)
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES


def filter_edges(edges: Iterable[MermaidEdge]) -> Iterable[MermaidEdge]:
    for edge in edges:
        if isinstance(edge.target, MermaidLiteral) and edge.source.title == edge.target.title:
            continue

        yield edge


def filter_nodes(edges: Iterable[MermaidEdge], except_uris: Iterable[NotLiteralNode]) -> Iterable[MermaidURINode | MermaidLiteral | MermaidBlankNode]:
    nodes = [
        node
        for edge in edges
        for node in edge.nodes
    ]

    literals_in_edges = {edge.target for edge in edges if isinstance(edge.target, MermaidLiteral)}
    for node in nodes:
        if isinstance(node, MermaidLiteral) and node not in literals_in_edges:
            continue

        if isinstance(node, MermaidURINode) and node.uri in except_uris:
            continue

        if isinstance(node, MermaidBlankNode) and node.node in except_uris:
            continue

        if isinstance(node, MermaidSubgraph):
            continue

        yield node


class Mermaid(Facet[str]):
    """Mermaid diagram."""

    META = Path(__file__).parent / 'mermaid.yamlld'

    def as_mermaid(self, node: Node):
        match node:
            case URIRef() as uri:
                if uri in self.subgraph_uris:
                    return MermaidSubgraph(children=[], uri=uri, title=self.render(uri, as_datatype=DATATYPES.title))

                return MermaidURINode(uri=uri, url=AnyUrl(uri), title=self.render(uri, as_datatype=DATATYPES.title))
            case Literal() as literal:
                return MermaidLiteral(literal=literal)
            case BNode() as bnode:
                return MermaidBlankNode(node=bnode, title=self.render(bnode, as_datatype=DATATYPES.title))
            case unknown:
                unknown_type = type(unknown)
                raise ValueError(f'Unknown something: {unknown} ({unknown_type})')

    def construct_mermaid_for_graph(self, graph: URIRef) -> Iterable[MermaidScalar]:
        """Render graph as mermaid."""
        rows = self.stored_query('graph.sparql', this=graph)
        edges = [
            MermaidEdge(
                source=self.as_mermaid(row['s']),
                target=self.as_mermaid(row['o']),
                title=self.render(row['p'], as_datatype=DATATYPES.title),
                predicate=row['p'],
            ) for row in rows
        ]

        edges = list(filter_edges(edges))
        nodes = list(
            filter_nodes(
                edges=edges,
                except_uris=self.subgraph_uris,
            ),
        )

        return *nodes, *edges

    @functools.cached_property
    def subgraph_uris(self) -> set[NotLiteralNode]:
        return set(
            funcy.pluck(
                'subgraph',
                self.stored_query('subgraphs.sparql', this=self.this),
            ),
        )

    def construct_mermaid_subgraphs(self) -> Iterable[MermaidSubgraph]:
        for subgraph_uri in self.subgraph_uris:
            children = list(self.construct_mermaid_for_graph(subgraph_uri))
            if children:
                title = self.render(subgraph_uri, as_datatype=DATATYPES.title)
                yield MermaidSubgraph(
                    children=children,
                    uri=subgraph_uri,
                    title=title,
                )

    def show(self) -> str:
        """Render mermaid diagram."""
        direct_children = self.construct_mermaid_for_graph(self.this)
        subgraphs = self.construct_mermaid_subgraphs()
        return str(Diagram(children=[*direct_children, *subgraphs]))



