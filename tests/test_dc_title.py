from rdflib import URIRef

from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def test_dc_elements_title_http():
    """DC Elements `title` term renders its human-readable label."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef('http://purl.org/dc/elements/1.1/title'),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == 'Title', f"Expected 'Title', got '{rendered_output}'"


def test_dc_elements_title_https():
    """HTTPS DC Elements `title` normalizes and renders its label."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef('https://purl.org/dc/elements/1.1/title'),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == 'Title', f"Expected 'Title', got '{rendered_output}'"


def test_dc_terms_title_http():
    """DC Terms `title` term renders its human-readable label."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef('http://purl.org/dc/terms/title'),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == 'Title', f"Expected 'Title', got '{rendered_output}'"


def test_dc_terms_title_https():
    """HTTPS DC Terms `title` normalizes and renders its label."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef('https://purl.org/dc/terms/title'),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == 'Title', f"Expected 'Title', got '{rendered_output}'"
