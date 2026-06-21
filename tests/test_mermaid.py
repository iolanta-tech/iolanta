import json
import re
from pathlib import Path

from pydantic import AnyUrl
from rdflib import Literal, URIRef

from iolanta.cli.main import decode_datatype
from iolanta.cli.main import render_and_return
from iolanta.conversions import path_to_iri
from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.mermaid.models import MermaidEdge, MermaidLiteral, MermaidURINode
from iolanta.namespaces import DATATYPES

RDF_MERMAID = URIRef("https://iolanta.tech/mermaid/rdf")


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
    rendered_output = (
        Iolanta()
        .add(source_file)
        .render(
            node=path_to_iri(source_file),
            as_datatype=DATATYPES.mermaid,
        )
    )

    assert "Literal-" not in rendered_output
    assert "Literal_" in rendered_output
    assert "literal value" in rendered_output
    assert f'{source_node_id}("example.org/source-node")' in rendered_output
    assert (
        f'click {source_node_id} "https://example.org/source-node"' in rendered_output
    )
    assert f"{source_node_id} --- Edge_" in rendered_output


def test_rendered_mermaid_prepends_resource_icons(tmp_path):
    source_file = tmp_path / "example.jsonld"
    source_file.write_text(
        json.dumps(
            {
                "@context": {
                    "ex": "https://example.org/",
                    "iolanta": "https://iolanta.tech/",
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "schema": "https://schema.org/",
                },
                "@id": "ex:alice",
                "@included": [
                    {
                        "@id": "schema:Person",
                        "iolanta:icon": "🧑",
                        "rdfs:label": "Person",
                    },
                    {
                        "@id": "rdf:type",
                        "iolanta:icon": "∈",
                        "rdfs:label": "type",
                    },
                ],
                "@type": "schema:Person",
                "schema:name": "Alice",
            },
        ),
    )

    rendered_output = (
        Iolanta()
        .add(source_file)
        .render(
            node=path_to_iri(source_file),
            as_datatype=DATATYPES.mermaid,
        )
    )

    assert "🧑 Person" in rendered_output
    assert "∈ type" in rendered_output


def test_mermaid_rdf_selects_raw_rdf_facet(tmp_path):
    source_file = tmp_path / "example.jsonld"
    source_file.write_text(
        json.dumps(
            {
                "@context": {
                    "ex": "https://example.org/",
                },
                "@id": "ex:alice",
                "ex:predicate": "Alice",
            },
        ),
    )
    iolanta = Iolanta().add(source_file)

    found = FacetFinder(
        iolanta=iolanta,
        node=path_to_iri(source_file),
        as_datatype=RDF_MERMAID,
    ).facet_and_output_datatype

    assert found["facet"] == URIRef("pkg:pypi/iolanta#mermaid-rdf")


def test_rendered_mermaid_rdf_shows_graph_triples(tmp_path):
    source_file = tmp_path / "example.jsonld"
    source_file.write_text(
        json.dumps(
            {
                "@context": {
                    "ex": "https://example.org/",
                    "iolanta": "https://iolanta.tech/",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "schema": "https://schema.org/",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                },
                "@graph": [
                    {
                        "@id": "ex:predicate",
                        "iolanta:icon": "∗",
                        "rdfs:label": "Predicate title",
                    },
                    {
                        "@id": "ex:alice",
                        "ex:predicate": [
                            {"@value": "42", "@type": "xsd:integer"},
                            {"@value": "2026-06-21", "@type": "xsd:date"},
                            {"@value": "Hello", "@language": "en"},
                            {"@id": "_:profile"},
                        ],
                        "rdfs:label": "Alice",
                        "schema:name": "Alice",
                    },
                    {
                        "@id": "_:profile",
                        "ex:active": {"@value": True, "@type": "xsd:boolean"},
                    },
                ],
            },
        ),
    )

    rendered_output = (
        Iolanta()
        .add(source_file)
        .render(
            node=path_to_iri(source_file),
            as_datatype=RDF_MERMAID,
        )
    )

    assert "🔢 42" in rendered_output
    assert "🇺🇸 Hello" in rendered_output
    assert "📅 2026-06-21" in rendered_output
    assert "✅ true" in rendered_output
    assert '[["Predicate title"]]' in rendered_output
    assert '[["∗"]]' in rendered_output
    assert "w3.org/2000/01/rdf-schema#label" in rendered_output
    assert "iolanta.tech/icon" in rendered_output
    assert re.search(r'\n  B[0-9a-f]{12}\("⬜ _:', rendered_output)
    assert (
        'click https___example_org_alice "https://example.org/alice"' in rendered_output
    )
    assert "click Edge_" in rendered_output
    assert (
        "click Edge_" in rendered_output and "example.org/predicate" in rendered_output
    )
    assert 'https___example_org_alice("example.org/alice")' in rendered_output
    assert "∗ Predicate title" not in rendered_output
    assert "&lt;https://example.org/alice&gt;" not in rendered_output
    assert '"42"^^' not in rendered_output
    assert '"Hello"@en' not in rendered_output
    assert "^^<http://www.w3.org/2001/XMLSchema#string>" not in rendered_output


def test_rendered_mermaid_rdf_example_yamlld():
    example_path = Path(__file__).parents[1] / "docs/mermaid/rdf-example.yamlld"
    rendered_output = (
        Iolanta()
        .add(example_path)
        .render(
            node=path_to_iri(example_path),
            as_datatype=RDF_MERMAID,
        )
    )

    assert "graph LR" in rendered_output
    assert '[["Ally"]]' in rendered_output
    assert '[["Alice"]]' in rendered_output
    assert '[["🔢 42"]]' in rendered_output
    assert "🇺🇸 Hello" in rendered_output
    assert "📅 2026-06-21" in rendered_output
    assert "✅ true" in rendered_output
    assert "⬜" in rendered_output
    assert '[["_:profile"]]' not in rendered_output
    assert re.search(
        r'profile"\]\)--> B[0-9a-fA-F]{12}',
        rendered_output,
    )
    assert 'https___example_org_alice("example.org/alice")' in rendered_output
    assert "&lt;" not in rendered_output
    assert '["<file://' not in rendered_output


def test_cli_shorthand_renders_mermaid_rdf(tmp_path):
    source_file = tmp_path / "example.jsonld"
    source_file.write_text(
        json.dumps(
            {
                "@context": {
                    "ex": "https://example.org/",
                },
                "@id": "ex:alice",
                "ex:predicate": "Alice",
            },
        ),
    )

    rendered_output = render_and_return(
        node=path_to_iri(source_file),
        as_datatype="mermaid/rdf",
    )

    assert 'https___example_org_alice("example.org/alice")' in rendered_output
    assert "example.org/predicate" in rendered_output
    assert "&lt;https://example.org/alice&gt;" not in rendered_output


def test_mkdocs_filter_shorthand_resolves_mermaid_rdf():
    assert decode_datatype("mermaid/rdf") == RDF_MERMAID
