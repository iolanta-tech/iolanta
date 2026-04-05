from __future__ import annotations

import functools
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

import funcy
from pydantic import AnyUrl
from rdflib import Literal, URIRef
from rdflib.term import Node

from iolanta import Facet
from iolanta.mermaid.models import (
    DATATYPE_ICONS,
    Diagram,
    Direction,
    MermaidArrowEdge,
    MermaidEdge,
    MermaidHTMLNode,
    MermaidLabelNode,
    MermaidLiteral,
    MermaidPlainEdge,
    MermaidScalar,
    MermaidSubgraph,
    MermaidTextNode,
    MermaidURINode,
)
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES, NP, RDFS

MAX_LITERAL_LENGTH = 42
SIGNATURE_PREDICATES = {
    URIRef("http://purl.org/nanopub/x/hasPublicKey"): "🔑",
    URIRef("http://purl.org/nanopub/x/hasSignature"): "✍️",
    URIRef("http://purl.org/nanopub/x/hasAlgorithm"): "⚙️",
}
COMPONENT_LABELS = {
    "assertion": "Assertion",
    "provenance": "Provenance",
    "pubinfo": "PubInfo",
}

COMPONENTS_QUERY = """
SELECT ?assertion ?provenance ?pubinfo WHERE {
    $this $has_assertion ?assertion ;
        $has_provenance ?provenance ;
        $has_publication_info ?pubinfo .
}
"""

GRAPH_QUERY = """
SELECT ?s ?p ?o WHERE {
    GRAPH $graph {
        ?s ?p ?o .
    }
}
"""


@dataclass(frozen=True)
class GraphTriple:
    subject: Node
    predicate: URIRef
    object_: Node


class TruncatedLiteral(MermaidLiteral):
    """{self.id}[["{self.title}"]]"""

    display_title: str

    @property
    def title(self) -> str:
        return self.display_title


class NanopublicationMermaidFacet(Facet[str]):
    """Hierarchical Mermaid renderer for nanopublications."""

    META = Path(__file__).parent / "nanopublication_mermaid.yamlld"

    def show(self) -> str:
        """Render a nanopublication as a hierarchical Mermaid diagram."""
        diagram = Diagram(
            direction=Direction.TB,
            children=[self.nanopublication_subgraph],
        )
        return str(diagram)

    @functools.cached_property
    def components(self) -> dict[str, URIRef]:
        row = funcy.first(
            self.query(
                COMPONENTS_QUERY,
                this=self.this,
                has_assertion=NP.hasAssertion,
                has_provenance=NP.hasProvenance,
                has_publication_info=NP.hasPublicationInfo,
            )
        )
        if not row:
            raise ValueError(f"Nanopublication structure is incomplete for {self.this}")
        return {
            "assertion": row["assertion"],
            "provenance": row["provenance"],
            "pubinfo": row["pubinfo"],
        }

    @functools.cached_property
    def nanopublication_title(self) -> str:
        short_id = str(self.this).rstrip("/").split("/")[-1]
        return f"Nanopublication {short_id[:12]}…"

    @functools.cached_property
    def nanopublication_subgraph(self) -> MermaidSubgraph:
        return MermaidSubgraph(
            children=[
                self.nanopublication_marker,
                self.assertion_subgraph,
                self.provenance_table_node,
                self.pubinfo_table_node,
                MermaidArrowEdge(
                    source=self.assertion_subgraph,
                    target=self.provenance_table_node,
                ),
                MermaidArrowEdge(
                    source=self.nanopublication_marker,
                    target=self.pubinfo_table_node,
                ),
            ],
            uri=self.this,
            title=self.nanopublication_title,
            direction=Direction.TB,
        )

    @functools.cached_property
    def nanopublication_marker(self) -> MermaidLabelNode:
        return MermaidLabelNode(
            name=f"{self.this}#marker",
            title="● Nanopublication",
            url=AnyUrl(str(self.this)),
        )

    @functools.cached_property
    def assertion_reference(self) -> MermaidSubgraph:
        return self.subgraph_reference(
            self.components["assertion"],
            COMPONENT_LABELS["assertion"],
        )

    @functools.cached_property
    def local_labels(self) -> dict[NotLiteralNode, str]:
        labels: dict[NotLiteralNode, str] = {}
        for component_uri in self.components.values():
            for row in self.query(
                """
                SELECT ?node ?label WHERE {
                    GRAPH $graph {
                        ?node rdfs:label ?label .
                    }
                    FILTER(!lang(?label) || lang(?label) = $language)
                }
                """,
                graph=component_uri,
                language=self.iolanta.language,
            ):
                labels[row["node"]] = str(row["label"])
        return labels

    @functools.cached_property
    def assertion_subgraph(self) -> MermaidSubgraph:
        return MermaidSubgraph(
            children=self.component_mermaid(self.components["assertion"]),
            uri=self.components["assertion"],
            title=COMPONENT_LABELS["assertion"],
            direction=Direction.LR,
        )

    def triples_for_graph(self, graph: URIRef) -> list[GraphTriple]:
        return [
            GraphTriple(
                subject=row["s"],
                predicate=row["p"],
                object_=row["o"],
            )
            for row in self.query(GRAPH_QUERY, graph=graph)
        ]

    def component_mermaid(self, graph: URIRef) -> list[MermaidScalar]:
        nodes: dict[str, MermaidScalar] = {}
        edges: list[MermaidEdge] = []
        for triple in self.triples_for_graph(graph):
            if triple.predicate == RDFS.label:
                continue
            source = self.visible_node(triple.subject, triple.predicate)
            target = self.visible_node(triple.object_, triple.predicate)
            if source is not None and not isinstance(source, MermaidSubgraph):
                nodes[source.id] = source
            if target is not None and not isinstance(target, MermaidSubgraph):
                nodes[target.id] = target
            if source is None or target is None:
                continue
            edges.append(
                MermaidEdge(
                    source=source,
                    target=target,
                    title=self.predicate_title(triple.predicate),
                    predicate=triple.predicate,
                ),
            )
        return [*nodes.values(), *edges]

    @functools.cached_property
    def provenance_table_node(self) -> MermaidHTMLNode:
        rows: list[str] = []
        seen_rows: set[tuple[str, str]] = set()

        for triple in self.triples_for_graph(self.components["provenance"]):
            row = (
                self.predicate_title(triple.predicate),
                self.metadata_value_html(triple.object_, triple.predicate),
            )
            if row in seen_rows:
                continue
            seen_rows.add(row)
            rows.append(
                "<tr>"
                f"<td>{html.escape(row[0])}</td>"
                f"<td>{row[1]}</td>"
                "</tr>",
            )

        table_html = (
            "<div style='font-weight:600;margin-bottom:0.5em'>Provenance</div>"
            "<table style='border-collapse:collapse'>"
            "<tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )
        return MermaidHTMLNode(
            name=f"{self.components['provenance']}#table",
            html=table_html,
        )

    @functools.cached_property
    def pubinfo_table_node(self) -> MermaidHTMLNode:
        rows: list[str] = []
        for triple in self.triples_for_graph(self.components["pubinfo"]):
            if triple.predicate == URIRef("http://purl.org/nanopub/x/hasSignatureTarget"):
                continue
            rows.append(
                (
                    "<tr>"
                    f"<td>{html.escape(self.predicate_title(triple.predicate))}</td>"
                    f"<td>{self.pubinfo_value_html(triple.object_, triple.predicate)}</td>"
                    "</tr>"
                ),
            )

        table_html = (
            "<div style='font-weight:600;margin-bottom:0.5em'>PubInfo</div>"
            "<table style='border-collapse:collapse'>"
            "<tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )
        return MermaidHTMLNode(
            name=f"{self.components['pubinfo']}#table",
            html=table_html,
        )

    def visible_node(
        self,
        node: Node,
        predicate: URIRef | None = None,
    ) -> MermaidScalar | None:
        match node:
            case URIRef() as uri:
                if uri == self.this:
                    return None
                if component_subgraph := self.folded_component_subgraph(uri):
                    return component_subgraph
                if uri in self.components.values():
                    return self.component_subgraph_for_uri(uri)
                return self.uri_node(uri)
            case Literal() as literal:
                return self.literal_node(literal, predicate=predicate)
            case _:
                return None

    def component_subgraph_for_uri(self, uri: URIRef) -> MermaidSubgraph:
        for component_name, component_uri in self.components.items():
            if component_uri == uri:
                return getattr(self, f"{component_name}_reference")
        raise ValueError(f"Unknown component URI: {uri}")

    def folded_component_subgraph(self, uri: URIRef) -> MermaidSubgraph | None:
        uri_text = str(uri)
        for component_name, component_uri in self.components.items():
            component_text = str(component_uri)
            if uri == component_uri:
                return getattr(self, f"{component_name}_reference")
            if uri == self.head_graph_reference(component_name):
                return getattr(self, f"{component_name}_reference")
            if uri_text.startswith(f"{component_text}#"):
                return getattr(self, f"{component_name}_reference")
        return None

    def head_graph_reference(self, component_name: str) -> URIRef:
        return URIRef(f"{self.this}/Head#{self.components[component_name]}")

    def subgraph_reference(self, uri: URIRef, title: str) -> MermaidSubgraph:
        return MermaidSubgraph(children=[], uri=uri, title=title)

    def uri_node(self, uri: URIRef, title: str | None = None) -> MermaidURINode:
        node_title = title or self.node_title(uri)
        return MermaidURINode(
            uri=uri,
            url=AnyUrl(str(uri)),
            title=node_title,
        )

    def literal_node(
        self,
        literal: Literal,
        predicate: URIRef | None = None,
    ) -> MermaidLiteral:
        if predicate in SIGNATURE_PREDICATES:
            display_value = self.truncate(str(literal))
            return TruncatedLiteral(
                literal=literal,
                display_title=f"{SIGNATURE_PREDICATES[predicate]} {display_value}",
            )

        icon = DATATYPE_ICONS.get(literal.datatype, "")
        title = self.truncate(str(literal))
        if icon:
            title = f"{icon} {title}"
        return TruncatedLiteral(
            literal=literal,
            display_title=title.replace('"', "\u201c").replace("'", "\u2019"),
        )

    def node_title(self, node: NotLiteralNode) -> str:
        if label := self.local_labels.get(node):
            return label
        rendered = str(self.render(node, as_datatype=DATATYPES.title))
        if rendered != str(node):
            return rendered
        return self.compact_uri_label(node)

    def predicate_title(self, predicate: URIRef) -> str:
        rendered = str(self.render(predicate, as_datatype=DATATYPES.title))
        if rendered != str(predicate):
            return rendered
        return self.compact_predicate_label(predicate)

    def metadata_value_html(
        self,
        node: Node,
        predicate: URIRef,
    ) -> str:
        match node:
            case URIRef() as uri:
                title = html.escape(self.node_title(uri))
                return f'<a href="{html.escape(str(uri), quote=True)}">{title}</a>'
            case Literal() as literal:
                return html.escape(self.literal_node(literal, predicate=predicate).title)
            case _:
                return html.escape(str(node))

    def pubinfo_value_html(
        self,
        node: Node,
        predicate: URIRef,
    ) -> str:
        return self.metadata_value_html(node, predicate)

    def compact_uri_label(self, uri: URIRef) -> str:
        parsed = urlparse(str(uri))
        path = unquote(parsed.path.rstrip("/"))
        if path:
            tail = path.split("/")[-1]
        else:
            tail = parsed.netloc or str(uri)
        if parsed.netloc.endswith("w3id.org") and "/np/" in path:
            return tail
        if parsed.netloc:
            return f"{parsed.netloc}/{tail}" if tail else parsed.netloc
        return str(uri)

    def compact_predicate_label(self, predicate: URIRef) -> str:
        parsed = urlparse(str(predicate))
        local_name = unquote(parsed.fragment or parsed.path.rstrip("/").split("/")[-1])
        words = re.sub(r"(?<!^)(?=[A-Z])", " ", local_name).replace("-", " ")
        return words.lower()

    def truncate(self, value: str) -> str:
        if len(value) <= MAX_LITERAL_LENGTH:
            return value
        visible = MAX_LITERAL_LENGTH // 2 - 2
        return f"{value[:visible]}…{value[-visible:]}"
