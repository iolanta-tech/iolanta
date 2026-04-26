import pytest
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import RDFS

from iolanta.facets.prov_value_title import ProvValueTitle
from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES, PROV


@pytest.mark.parametrize(
    ("url", "expected_title"),
    [
        ("http://purl.org/dc/elements/1.1/title", "Title"),  # noqa: WPS226
        ("https://purl.org/dc/elements/1.1/title", "Title"),
        ("http://purl.org/dc/terms/title", "Title"),
        ("https://purl.org/dc/terms/title", "Title"),
        ("https://www.wikidata.org/entity/Q24229338", "Rhysling"),
        ("http://www.wikidata.org/entity/Q24229338", "Rhysling"),
        ("https://wikidata.org/entity/Q24229338", "Rhysling"),
        (
            "http://www.wikidata.org/prop/direct/P397",
            "parent astronomical body",
        ),
        ("https://orcid.org/0009-0001-8740-4213", "Anatoly Scherbakov"),
    ],
)
def test_title_rendering(url: str, expected_title: str):
    """Important linked-data URLs must render readable titles."""
    rendered_output = Iolanta().render(
        URIRef(url),
        as_datatype=DATATYPES.title,
    )

    assert rendered_output == expected_title


def test_orcid_title_uses_person_title_facet():
    """ORCID profiles must use the person-specific title facet."""
    facet = FacetFinder(
        iolanta=Iolanta(),
        node=URIRef("https://orcid.org/0009-0001-8740-4213"),
        as_datatype=DATATYPES.title,
    ).facet_and_output_datatype

    assert str(facet["facet"]) == "pkg:pypi/iolanta#title-foaf-person"


def test_prov_value_title_renders_source():
    """PROV value blank nodes should render as value sourced from reference."""
    iolanta = Iolanta()
    node = BNode()
    source = URIRef("https://example.com/rfc-8259-section-8-1")
    iolanta.graph.add((node, PROV.value, Literal(True)))
    iolanta.graph.add((node, PROV.wasDerivedFrom, source))
    iolanta.graph.add((source, RDFS.label, Literal("RFC 8259 section 8.1")))

    rendered_output = ProvValueTitle(
        this=node,
        iolanta=iolanta,
        as_datatype=DATATYPES.title,
    ).show()

    assert rendered_output == "true ⇐ RFC 8259 section 8.1"


def test_prov_value_title_filters_by_language():
    """PROV value titles should follow the configured output language."""
    iolanta = Iolanta(language=Literal("en"))
    node = BNode()
    source = URIRef("https://example.com/source")
    iolanta.graph.add((node, PROV.value, Literal("vrai", lang="fr")))
    iolanta.graph.add((node, PROV.value, Literal("true", lang="en")))
    iolanta.graph.add((node, PROV.wasDerivedFrom, source))
    iolanta.graph.add((source, RDFS.label, Literal("Source anglaise", lang="fr")))
    iolanta.graph.add((source, RDFS.label, Literal("English source", lang="en")))

    rendered_output = ProvValueTitle(
        this=node,
        iolanta=iolanta,
        as_datatype=DATATYPES.title,
    ).show()

    assert rendered_output == "true ⇐ English source"


def test_prov_value_title_facet_is_selected():
    """PROV value blank nodes should use the specialized title facet."""
    iolanta = Iolanta()
    iolanta.add(ProvValueTitle.META)
    node = BNode()
    iolanta.graph.add((node, PROV.value, Literal(True)))
    iolanta.graph.add(
        (
            node,
            PROV.wasDerivedFrom,
            URIRef("https://example.com/rfc-8259-section-8-1"),
        ),
    )

    facet = FacetFinder(
        iolanta=iolanta,
        node=node,
        as_datatype=DATATYPES.title,
    ).facet_and_output_datatype

    assert str(facet["facet"]) == "pkg:pypi/iolanta#title-prov-value"
