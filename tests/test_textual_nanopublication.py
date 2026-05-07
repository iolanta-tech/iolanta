"""Tests for Textual nanopublication rendering support."""

from importlib import import_module

from rdflib import Literal, URIRef
from rdflib.namespace import XSD

from iolanta.iolanta import Iolanta
from iolanta.namespaces import DCTERMS, NP
from iolanta.sparqlspace.processor import GlobalSPARQLProcessor


def test_nanopublication_query_declares_prefixes(monkeypatch):
    """Ensure the query runs without graph prefixes.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        GlobalSPARQLProcessor,
        'load',
        lambda _processor, _source: None,
    )

    nanopublication = URIRef('https://example.org/np/RA-test')
    assertion = URIRef('https://example.org/np/RA-test/assertion')
    created_time = Literal(
        '2026-05-07T14:33:34.514Z',
        datatype=XSD.dateTime,
    )

    iolanta = Iolanta()
    iolanta.graph.add((nanopublication, NP.hasAssertion, assertion))
    iolanta.graph.add((nanopublication, DCTERMS.created, created_time))

    rows = iolanta.query(
        import_module(
            'iolanta.facets.textual_nanopublication.nanopublication_widget',
        ).NANOPUBLICATION_QUERY,
        uri=nanopublication,
    )

    assert rows == [
        {
            'assertion': assertion,
            'created_time': created_time,
        },
    ]
