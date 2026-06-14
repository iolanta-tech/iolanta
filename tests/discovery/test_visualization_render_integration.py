"""Render integration tests for visualization index loading."""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

from iolanta.facets.textual_ontology.facets import OntologyFacet
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES, VANN
from iolanta.sparqlspace.processor import normalize_term


@dataclass
class _LeafFacet:
    """Facet used for the nested render target."""

    this: object
    iolanta: Iolanta
    as_datatype: object = None

    def show(self) -> str:
        return "leaf"


@dataclass
class _NestedRenderFacet:
    """Minimal facet that triggers a nested render during show()."""

    this: object
    iolanta: Iolanta
    as_datatype: object = None

    def show(self) -> str:
        self.iolanta.render(
            normalize_term("https://example.org/nested"),
            as_datatype=DATATYPES.title,
        )
        return "nested"


def _sample_urls() -> list[str]:
    return ["http://purl.org/np/RA-test-nanopub-1"]


def _inject_ontology_groups(iolanta: Iolanta) -> None:
    ontology = URIRef("https://example.org/ontology")
    datatype_group = URIRef("https://example.org/groups/datatype")
    property_term = URIRef("https://example.org/terms/property")
    iolanta.graph.add((ontology, RDF.type, OWL.Ontology))
    iolanta.graph.add((ontology, VANN.termGroup, datatype_group))
    iolanta.graph.add(
        (datatype_group, RDFS.label, Literal("Datatype", datatype=XSD.string)),
    )
    iolanta.graph.add((property_term, RDFS.isDefinedBy, ontology))
    iolanta.graph.add((property_term, RDF.type, datatype_group))


@pytest.fixture()
def patched_discovery(monkeypatch):
    fetch_calls: list[object] = []
    load_calls: list[object] = []

    def fetch_visualization_index(*_args, **_kwargs):
        fetch_calls.append(object())
        return _sample_urls()

    def load_visualization_index(iolanta, nanopub_urls):
        load_calls.append((iolanta, nanopub_urls))
        _inject_ontology_groups(iolanta)
        return len(nanopub_urls)

    monkeypatch.setattr(
        "iolanta.discovery.visualization_nanopublications.fetch_visualization_index",
        fetch_visualization_index,
    )
    monkeypatch.setattr(
        "iolanta.discovery.visualization_nanopublications.load_visualization_index",
        load_visualization_index,
    )
    return fetch_calls, load_calls


def test_first_render_loads_index_once(patched_discovery):
    fetch_calls, load_calls = patched_discovery
    iolanta = Iolanta()

    iolanta.render(
        URIRef("https://example.org/ontology"),
        as_datatype=DATATYPES.title,
    )

    assert len(fetch_calls) == 1
    assert len(load_calls) == 1


def test_repeated_renders_do_not_reload(patched_discovery):
    fetch_calls, load_calls = patched_discovery
    iolanta = Iolanta()

    iolanta.render(
        URIRef("https://example.org/ontology"),
        as_datatype=DATATYPES.title,
    )
    iolanta.render(
        URIRef("https://example.org/other"),
        as_datatype=DATATYPES.title,
    )

    assert len(fetch_calls) == 1
    assert len(load_calls) == 1


def test_nested_render_does_not_reload(monkeypatch, patched_discovery):
    fetch_calls, load_calls = patched_discovery
    render_calls = {"count": 0}

    def facet_finder(**_kwargs):
        render_calls["count"] += 1
        facet_finder_result = MagicMock()
        facet_finder_result.facet_and_output_datatype = {
            "facet": URIRef("https://example.org/test-facet"),
            "output_datatype": DATATYPES.title,
        }
        return facet_finder_result

    monkeypatch.setattr("iolanta.iolanta.FacetFinder", facet_finder)

    iolanta = Iolanta()
    mock_resolver = MagicMock()
    mock_resolver.resolve.side_effect = (
        lambda _iri: _NestedRenderFacet if render_calls["count"] == 1 else _LeafFacet
    )
    iolanta.facet_resolver = mock_resolver

    iolanta.render(
        URIRef("https://example.org/ontology"),
        as_datatype=DATATYPES.title,
    )

    assert render_calls["count"] == 2
    assert len(fetch_calls) == 1
    assert len(load_calls) == 1


def test_ontology_render_uses_loaded_groups(patched_discovery):
    iolanta = Iolanta()
    iolanta._ensure_visualization_index_loaded()

    facet = OntologyFacet(
        this=URIRef("https://example.org/ontology"),
        iolanta=iolanta,
        as_datatype=DATATYPES.title,
    )
    grouped = facet.grouped_terms

    datatype_group = URIRef("https://example.org/groups/datatype")
    assert datatype_group in grouped
    assert grouped[datatype_group][0].term == URIRef(
        "https://example.org/terms/property",
    )
