import json
import re

from pydantic import AnyUrl
from rdflib import Literal, URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta
from iolanta.mermaid.models import MermaidEdge, MermaidLiteral, MermaidURINode
from iolanta.namespaces import DATATYPES


def test_literal_node_id_is_mermaid_11_safe():
    literal = MermaidLiteral(literal=Literal("literal value"))

    assert literal.id.startswith("Literal_")
    assert "Literal-" not in literal.id
    assert re.match(r"^[A-Za-z_][0-9A-Za-z_]*$", literal.id)
    assert str(literal) == f'{literal.id}[["literal value"]]'


def test_uri_node_id_and_click_line_are_mermaid_11_safe():
    uri = URIRef("https://example.org/source-node")
    node = MermaidURINode(
        uri=uri,
        url=AnyUrl(str(uri)),
        title="Source node",
    )

    assert node.id == "https___example_org_source_node"
    assert f'click {node.id} "{uri}"' in str(node)
    assert "source-node" not in node.id


def test_edge_id_is_mermaid_11_safe_and_clickable():
    source = MermaidURINode(
        uri=URIRef("https://example.org/source-node"),
        url=AnyUrl("https://example.org/source-node"),
        title="Source node",
    )
    target = MermaidLiteral(literal=Literal("literal value"))
    edge = MermaidEdge(
        source=source,
        target=target,
        predicate=URIRef("https://example.org/hyphen-predicate"),
        title="hyphen-predicate",
    )

    assert edge.id.startswith("Edge_")
    assert re.match(r"^[A-Za-z_][0-9A-Za-z_]*$", edge.id)
    assert f'click {edge.id} "https://example.org/hyphen-predicate"' in str(edge)


def test_rendered_mermaid_sanitizes_internal_ids(tmp_path):
    source_file = tmp_path / "example.jsonld"
    source_file.write_text(
        json.dumps(
            {
                "@context": {
                    "ex": "https://example.org/",
                },
                "@id": "https://example.org/source-node",
                "ex:hyphen-predicate": "literal value",
            },
        ),
    )

    source_node_id = "https___example_org_source_node"
    rendered_output = Iolanta().add(source_file).render(
        node=path_to_iri(source_file),
        as_datatype=DATATYPES.mermaid,
    )

    assert "Literal-" not in rendered_output
    assert "Literal_" in rendered_output
    assert "literal value" in rendered_output
    assert f'{source_node_id}("example.org/source-node")' in rendered_output
    assert f'click {source_node_id} "https://example.org/source-node"' in rendered_output
    assert f"{source_node_id} --- Edge_" in rendered_output
