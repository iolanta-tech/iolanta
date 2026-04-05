from rdflib import URIRef

from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def test_orcid_title_uses_person_title_facet():
    iolanta = Iolanta()
    facet = FacetFinder(
        iolanta=iolanta,
        node=URIRef("https://orcid.org/0009-0001-8740-4213"),
        as_datatype=DATATYPES.title,
    ).facet_and_output_datatype

    assert str(facet["facet"]) == "pkg:pypi/iolanta#title-foaf-person"


def test_orcid_title_is_human_readable():
    """ORCID profiles render a human-readable title via the person facet."""
    iolanta = Iolanta()
    rendered_output = iolanta.render(
        URIRef("https://orcid.org/0009-0001-8740-4213"),
        as_datatype=DATATYPES.title,
    )
    assert rendered_output == "Anatoly Scherbakov", (
        f"Expected 'Anatoly Scherbakov', got '{rendered_output}'"
    )
