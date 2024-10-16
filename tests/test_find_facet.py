from dataclasses import asdict

import pytest
from boltons.iterutils import remap
from rdflib import XSD, Literal, URIRef

from iolanta.facets.errors import FacetNotFound
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA, LOCAL


def test_none(iolanta: Iolanta, env: URIRef):
    with pytest.raises(FacetNotFound):
        iolanta.render(
            LOCAL.boom,
            as_datatype=env,
        )


def test_direct(iolanta: Iolanta, facet_iri: str, env: URIRef):
    response, stack = iolanta.add({
        '$id': 'boom',
        'iolanta:facet': {
            '$id': facet_iri,
            'iolanta:outputs': env,
        },
    }).render(
        LOCAL.boom,
        as_datatype=env,
    )

    assert response == 'foo'

    comparable_stack = remap(
        asdict(stack),
        lambda p, key, v: key not in {'iolanta', 'stack_children'},
    )

    assert comparable_stack == {
        'node': LOCAL.boom,
        'facet': {
            'iri': LOCAL.boom,
            'environment': IOLANTA.test,
        },
        'children': [{
            'node': Literal('foo'),
            'facet': {
                'iri': Literal('foo'),
                'environment': IOLANTA.html,
            },
            'children': [],
        }],
    }


def test_instance_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': 'boom',
        'rdf:type': {
            'iolanta:hasInstanceFacet': {
                '$id': facet_iri,
                'iolanta:outputs': env,
            },
        },
    }).render(
        LOCAL.boom,
        as_datatype=env,
    )[0] == 'foo'


def test_default_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': env,
        'iolanta:hasDefaultFacet': {
            '$id': facet_iri,
            'iolanta:outputs': env,
        },
    }).render(
        LOCAL.boom,
        as_datatype=env,
    )[0] == 'foo'


def test_datatype_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    assert iolanta.add({
        '$id': XSD.string,
        'iolanta:hasDatatypeFacet': {
            '$id': facet_iri,
            'iolanta:outputs': env,
        },
    }).render(
        Literal('foo', datatype=XSD.string),
        as_datatype=env,
    )[0] == 'foo'


def test_null_datatype_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    with pytest.raises(FacetNotFound):
        iolanta.render(
            Literal('foo'),
            as_datatype=env,
        )
