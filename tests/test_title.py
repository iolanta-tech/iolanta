import pytest
from rdflib import URIRef

from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


@pytest.mark.parametrize(
    ("url", "expected_title"),
    [
        ("http://purl.org/dc/elements/1.1/title", "Title"),
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
