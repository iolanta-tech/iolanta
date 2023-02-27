from rdflib import URIRef

from iolanta.facet import Facet
from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA, LOCAL


class FooFacet(Facet[str]):

    def show(self) -> str:
        return 'foo'


def test_none():
    assert Iolanta(
        force_facets={
            URIRef('python://foo'): FooFacet,
        },
    ).add({
        '$id': 'boom',
    }).render(
        LOCAL.boom,
        environments=[IOLANTA.html],
    ) == 'Boom'
