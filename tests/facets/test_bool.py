from rdflib import XSD, Literal

from iolanta.iolanta import Iolanta


def test_bool():
    assert Iolanta().render(
        Literal('true', datatype=XSD.boolean),
    ) == '✔️'
