import pytest
from rdflib import XSD, Literal, URIRef

from iolanta.iolanta import Iolanta


@pytest.mark.parametrize(
    ['literal', 'icon'],
    [
        ['true', '✔️'],
        ['false', '❌'],
    ],
)
def test_bool(
    environment: URIRef,
    literal: str,
    icon: str,
):
    assert Iolanta().render(
        Literal(literal, datatype=XSD.boolean),
        environments=[environment],
    ) == icon
