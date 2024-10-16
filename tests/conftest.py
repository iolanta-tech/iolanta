import pytest
from rdflib import Literal, URIRef

from iolanta.facets.facet import Facet
from iolanta.facets.html import Default
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA


class FooFacet(Facet[str]):
    def show(self) -> str:
        return self.render(
            Literal('foo'),
            as_datatype=[IOLANTA.html],
        )


@pytest.fixture()
def facet_iri() -> str:
    return URIRef('python://FooFacet')


@pytest.fixture()
def env() -> URIRef:
    return IOLANTA.test


@pytest.fixture(params=[IOLANTA.html, IOLANTA.cli])
def environment(request):
    return request.param


@pytest.fixture()
def iolanta(facet_iri: URIRef) -> Iolanta:
    return Iolanta(
        facet_resolver={
            facet_iri: FooFacet,
            URIRef('python://iolanta.facets.html.Default'): Default,
        },
    )
