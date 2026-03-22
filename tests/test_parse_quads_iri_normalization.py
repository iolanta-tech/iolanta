"""Tests for IRI normalization in `parse_quads.parse_term`."""

from rdflib import URIRef

from iolanta.parse_quads import parse_term


def test_iri_spaces_in_path_encoded_for_commons_file_path():
    """Wikimedia-style paths with spaces become percent-encoded for rdflib."""
    term = {
        'type': 'IRI',
        'value': (
            'http://commons.wikimedia.org/wiki/Special:FilePath/'
            'PCI Express.svg'
        ),
    }
    node = parse_term(term, blank_node_prefix='')
    assert isinstance(node, URIRef)
    assert str(node) == (
        'http://commons.wikimedia.org/wiki/Special:FilePath/PCI%20Express.svg'
    )


def test_iri_percent_encoded_space_normalizes_consistently():
    """Input with %20 decodes then re-encodes to the same stable URI."""
    term = {
        'type': 'IRI',
        'value': (
            'http://commons.wikimedia.org/wiki/Special:FilePath/'
            'PCI%20Express.svg'
        ),
    }
    node = parse_term(term, blank_node_prefix='')
    assert str(node) == (
        'http://commons.wikimedia.org/wiki/Special:FilePath/PCI%20Express.svg'
    )


def test_iri_simple_https_unchanged():
    """Well-formed IRIs without problematic characters stay as-is."""
    term = {'type': 'IRI', 'value': 'https://example.com/foo'}
    node = parse_term(term, blank_node_prefix='')
    assert str(node) == 'https://example.com/foo'


def test_iri_n3_serializes_without_rdflib_invalid_chars():
    """Normalized http(s) IRIs work with ``URIRef.n3()`` (Turtle/N3)."""
    term = {
        'type': 'IRI',
        'value': (
            'http://commons.wikimedia.org/wiki/Special:FilePath/'
            'PCI Express.svg'
        ),
    }
    node = parse_term(term, blank_node_prefix='')
    assert node.n3().startswith('<http://')
