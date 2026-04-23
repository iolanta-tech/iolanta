from rdflib import URIRef

from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def test_textual_graph_preferred_over_properties():
    """Graph triples should be the default graph view."""
    ordering = FacetFinder(
        iolanta=Iolanta(),
        node=URIRef('urn:example:graph'),
        as_datatype=DATATYPES['textual'],
    ).retrieve_facets_preference_ordering()

    assert (
        URIRef('pkg:pypi/iolanta#textual-graph'),
        URIRef('pkg:pypi/iolanta#textual-properties'),
    ) in ordering
