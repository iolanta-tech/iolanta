import pytest
from rdflib import XSD, Literal, URIRef

from iolanta.facets.errors import FacetNotFound
from iolanta.iolanta import Iolanta
from iolanta.namespaces import LOCAL


def test_none(iolanta: Iolanta, env: URIRef):
    with pytest.raises(FacetNotFound):
        assert iolanta.render(
            LOCAL.boom,
            environments=[env],
        )


def test_direct(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': 'boom',
        'iolanta:facet': {
            '$id': facet_iri,
            'iolanta:supports': env,
        },
    }).render(
        LOCAL.boom,
        environments=[env],
    ) == 'foo'


def test_instance_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': 'boom',
        'rdf:type': {
            'iolanta:hasInstanceFacet': {
                '$id': facet_iri,
                'iolanta:supports': env,
            },
        },
    }).render(
        LOCAL.boom,
        environments=[env],
    ) == 'foo'


def test_default_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': env,
        'iolanta:hasDefaultFacet': {
            '$id': facet_iri,
            'iolanta:supports': env,
        },
    }).render(
        LOCAL.boom,
        environments=[env],
    ) == 'foo'


def test_datatype_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': XSD.string,
        'iolanta:hasDatatypeFacet': {
            '$id': facet_iri,
            'iolanta:supports': env,
        },
    }).render(
        Literal('foo', datatype=XSD.string),
        environments=[env],
    ) == 'foo'


def test_null_datatype_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    with pytest.raises(FacetNotFound):
        iolanta.render(
            Literal('foo'),
            environments=[env],
        )
