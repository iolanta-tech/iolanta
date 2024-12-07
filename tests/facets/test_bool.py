import pytest
from rdflib import Literal, URIRef

from iolanta.iolanta import Iolanta
from iolanta.namespaces import XSD


@pytest.mark.parametrize(
    ['literal', 'icon'],
    [
        ['true', '✔️'],
        ['false', '❌'],
    ],
)
def test_bool(
    as_datatype: URIRef,
    literal: str,
    icon: str,
):
    assert Iolanta().render(
        Literal(literal, datatype=XSD.boolean),
        as_datatype=as_datatype,
    )[0] == icon
