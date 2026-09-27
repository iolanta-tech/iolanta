"""Tests for the MkDocs ontology facet."""

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

from iolanta.facets.mkdocs_ontology.facet import MkDocsOntologyFacet
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA, VANN


def _title(_facet, node, as_datatype) -> str:
    """Render the labels used by the fixture graph."""
    return {
        "https://example.org/groups/properties": "Properties",
        "https://example.org/terms/property": "property",
        "https://example.org/terms/type": "type",
    }[str(node)]


def _rendered_card(monkeypatch, icons: tuple[str, ...]) -> str:
    """Render a grouped term card with the supplied icon literals."""
    ontology = URIRef("https://example.org/ontology")
    group = URIRef("https://example.org/groups/properties")
    term = URIRef("https://example.org/terms/type")
    iolanta = Iolanta()
    iolanta.graph.add((ontology, VANN.termGroup, group))
    iolanta.graph.add((term, RDFS.isDefinedBy, ontology))
    iolanta.graph.add((term, RDF.type, group))
    iolanta.graph.add(
        (
            URIRef("https://example.org/terms/property"),
            RDFS.isDefinedBy,
            ontology,
        ),
    )
    iolanta.graph.add(
        (
            URIRef("https://example.org/terms/property"),
            RDF.type,
            group,
        ),
    )

    for icon in icons:
        iolanta.graph.add((term, IOLANTA.icon, Literal(icon)))

    monkeypatch.setattr(
        MkDocsOntologyFacet,
        "render",
        _title,
    )

    return MkDocsOntologyFacet(this=ontology, iolanta=iolanta).show()


@pytest.mark.parametrize(
    ("icons", "expected", "unexpected"),
    [
        (("∈",), '<span aria-hidden="true">∈</span>', ""),
        ((), "__[type](https://example.org/terms/type)__", "aria-hidden"),
        (("z", "a"), '<span aria-hidden="true">a</span>', ">z<"),
        (("<span>",), "&lt;span&gt;", "<span><span>"),
    ],
)
def test_renders_literal_icons_safely(
    monkeypatch,
    icons: tuple[str, ...],
    expected: str,
    unexpected: str,
):
    """Render an icon when present without allowing it to alter card markup."""
    rendered = _rendered_card(monkeypatch, icons)

    assert expected in rendered
    if unexpected:
        assert unexpected not in rendered
