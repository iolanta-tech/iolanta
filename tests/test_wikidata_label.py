from rdflib import URIRef

from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def test_wikidata_rhysling_title():
    """Test that Wikidata entity Q24229338 renders as 'Rhysling' with --as title."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(  # noqa: WPS110
        URIRef("https://www.wikidata.org/entity/Q24229338"),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == "Rhysling", (
        f"Expected 'Rhysling', got '{rendered_output}'"
    )


def test_wikidata_rhysling_title_http():
    """Test that Wikidata entity Q24229338 renders as 'Rhysling' with --as title using http://."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(  # noqa: WPS110
        URIRef("http://www.wikidata.org/entity/Q24229338"),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == "Rhysling", (
        f"Expected 'Rhysling', got '{rendered_output}'"
    )


def test_wikidata_rhysling_title_bare_host_no_www():
    """Bare https://wikidata.org/entity/... must normalize to graph IRIs (www + http)."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef("https://wikidata.org/entity/Q24229338"),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == "Rhysling", (
        f"Expected 'Rhysling', got '{rendered_output}'"
    )


def test_wikidata_direct_property_title():
    """Wikidata direct property IRIs render their human-readable label."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef("http://www.wikidata.org/prop/direct/P397"),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == "parent astronomical body", (
        f"Expected 'parent astronomical body', got '{rendered_output}'"
    )
