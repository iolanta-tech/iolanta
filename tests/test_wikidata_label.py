import pytest
from rdflib import URIRef

from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def test_wikidata_rhysling_title():
    """Test that Wikidata entity Q24229338 renders as 'Rhysling' with --as title."""
    iolanta = Iolanta()
    result = iolanta.render(
        URIRef('https://www.wikidata.org/entity/Q24229338'),
        as_datatype=DATATYPES.title,
    )
    assert result == 'Rhysling', f"Expected 'Rhysling', got '{result}'"


def test_wikidata_rhysling_title_http():
    """Test that Wikidata entity Q24229338 renders as 'Rhysling' with --as title using http://."""
    iolanta = Iolanta()
    result = iolanta.render(
        URIRef('http://www.wikidata.org/entity/Q24229338'),
        as_datatype=DATATYPES.title,
    )
    assert result == 'Rhysling', f"Expected 'Rhysling', got '{result}'"
