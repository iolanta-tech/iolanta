from dataclasses import asdict

import pytest
from boltons.iterutils import remap
from rdflib import Literal, URIRef

from iolanta.facets.errors import FacetNotFound
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA, LOCAL, XSD


def test_none(iolanta: Iolanta, env: URIRef):
    with pytest.raises(FacetNotFound):
        iolanta.render(
            LOCAL.boom,
            as_datatype=env,
        )


def test_null_datatype_facet(iolanta: Iolanta, facet_iri: str, env: URIRef):
    with pytest.raises(FacetNotFound):
        iolanta.render(
            Literal('foo'),
            as_datatype=env,
        )
