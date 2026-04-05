from rdflib import URIRef

from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES, NP


def test_np_namespace_uses_http():
    assert str(NP) == "http://www.nanopub.org/nschema#"


def test_nanopublication_mermaid_is_hierarchical():
    rendered_output = Iolanta().render(
        node=URIRef(
            "https://w3id.org/np/RAQtNxM5sbzt7-4lGVzAMPQtT32wDUGJAqKJObwdbYNDs",
        ),
        as_datatype=DATATYPES.mermaid,
    )

    assert rendered_output.startswith("graph TB")
    assert "[\"Assertion\"]" in rendered_output
    assert "Provenance" in rendered_output
    assert "[\"Provenance\"]" not in rendered_output
    assert "PubInfo" in rendered_output
    assert "[\"PubInfo\"]" not in rendered_output
    assert "<<table" not in rendered_output
    assert "</table>>" not in rendered_output
    assert "Nanopublication RAQtNxM5sbzt" in rendered_output
    assert "Nanopublication" in rendered_output
    assert "has assertion" not in rendered_output
    assert "has provenance" not in rendered_output
    assert "has publication info" not in rendered_output
    assert "Anchor_" not in rendered_output
    assert "http___www_nanopub_org_nschema_Nanopublication" not in rendered_output
    assert "Head" not in rendered_output
    assert "provenance#https:" not in rendered_output
    assert "Jupiter" in rendered_output
    assert "Europa" in rendered_output
    assert "describes" in rendered_output
    assert "Anatoly Scherbakov" in rendered_output
    assert "✍️" in rendered_output
    assert "🔑" in rendered_output
    assert "⚙️" in rendered_output
    assert "…" in rendered_output


def test_nanopublication_mermaid_uses_instance_facet():
    iolanta = Iolanta()
    facet = FacetFinder(
        iolanta=iolanta,
        node=URIRef(
            "https://w3id.org/np/RAQtNxM5sbzt7-4lGVzAMPQtT32wDUGJAqKJObwdbYNDs",
        ),
        as_datatype=DATATYPES.mermaid,
    ).facet_and_output_datatype

    assert str(facet["facet"]) == "pkg:pypi/iolanta#mermaid-nanopublication"
