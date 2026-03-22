"""Regression: instance facet lookup with blank-node classes."""

from rdflib import BNode, URIRef
from rdflib.namespace import RDF, RDFS

from iolanta.facets.locator import FacetFinder
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA


def test_by_instance_facet_does_not_crash_with_blank_node_class(iolanta: Iolanta) -> None:
    """
    Merged `by_instance_facet` query must not interpolate BNodes as `<_:…>` IRIs.

    That used to make the SPARQL processor preload skolem URIs and raise, and
    could recurse badly during exception logging.
    """
    subject = URIRef('https://example.test/ns#subject')
    anonymous_class = BNode()
    iolanta.graph.add((subject, RDF.type, anonymous_class))
    iolanta.graph.add((subject, RDF.type, RDFS.Resource))

    rows = list(
        FacetFinder(
            iolanta=iolanta,
            node=subject,
            as_datatype=IOLANTA.test,
        ).by_instance_facet(),
    )

    assert isinstance(rows, list)
