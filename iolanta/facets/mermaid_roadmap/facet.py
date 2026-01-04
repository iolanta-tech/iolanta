from pathlib import Path
from typing import Iterable

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
from iolanta.namespaces import DATATYPES
from pydantic import AnyUrl
from rdflib import URIRef as RDFURIRef


class TaskNode(MermaidScalar):
    """A Mermaid node with attached CSS classes."""

    node: MermaidURINode | MermaidBlankNode | MermaidLiteral
    classes: list[str] = []

    def __str__(self) -> str:
        """Render the wrapped node."""
        return str(self.node)

    @property
    def id(self) -> str:
        """Get the ID of the wrapped node."""
        return self.node.id


class BlocksEdge(MermaidEdge):
    """
    {self.source.id} --> {self.target.id}
    """

    def __init__(self, source, target):
        # Initialize with empty title and a dummy predicate
        super().__init__(
            source=source,
            target=target,
            predicate=RDFURIRef('https://iolanta.tech/roadmap/blocks'),
            title='',
        )

    def __str__(self) -> str:
        # Override to remove intermediate node - just direct arrow
        return f'{self.source.id} --> {self.target.id}'


# Rebuild Pydantic models to resolve forward references
# Need to rebuild MermaidEdge first so MermaidSubgraph is available
MermaidEdge.model_rebuild()
BlocksEdge.model_rebuild()


class MermaidRoadmap(Facet[str]):
    """Mermaid roadmap diagram."""

    META = Path(__file__).parent / 'mermaid_roadmap.yamlld'

    inference_path = Path(__file__).parent / 'inference'

    def show(self) -> str:
        """Render mermaid roadmap diagram."""
        children = list(self.construct_mermaid_for_graph(self.this))
        
        # Extract class assignments from TaskNode instances
        tail_parts = ['classDef unblocked fill:#0a5,stroke:#063,stroke-width:2px,color:#fff;']
        for child in children:
            if isinstance(child, TaskNode) and child.classes:
                for class_name in child.classes:
                    tail_parts.append(f'class {child.id} {class_name}')
        
        tail = '\n'.join(tail_parts)
        
        return str(Diagram(
            children=children,
            tail=tail,
        ))

    def as_mermaid(self, node: Node):
        """Convert RDF node to Mermaid node."""
        match node:
            case URIRef() as uri:
                return MermaidURINode(
                    uri=uri,
                    url=AnyUrl(uri),
                    title=self.render(uri, as_datatype=DATATYPES.title),
                )
            case Literal() as literal:
                return MermaidLiteral(literal=literal)
            case BNode() as bnode:
                return MermaidBlankNode(
                    node=bnode,
                    title=self.render(bnode, as_datatype=DATATYPES.title),
                )
            case unknown:
                unknown_type = type(unknown)
                raise ValueError(f'Unknown node type: {unknown} ({unknown_type})')

    def construct_mermaid_for_graph(self, graph: URIRef) -> Iterable[MermaidScalar]:
        """Render graph as mermaid."""
        # Get nodes
        node_rows = self.stored_query('nodes.sparql')
        node_rows_list = list(node_rows)
        
        nodes = [
            TaskNode(
                node=self.as_mermaid(row['node']),
                classes=['unblocked'] if row.get('is_unblocked', False) else [],
            )
            for row in node_rows_list
        ]

        # Get edges for roadmap:blocks relationships
        edge_rows = self.stored_query('edges.sparql')
        edge_rows_list = list(edge_rows)
        
        edges = [
            BlocksEdge(
                source=self.as_mermaid(row['source']),
                target=self.as_mermaid(row['target']),
            )
            for row in edge_rows_list
        ]

        return [*nodes, *edges]
