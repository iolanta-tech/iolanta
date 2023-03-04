from rdflib import URIRef

from iolanta.facets.generic.bool_literal import BoolLiteral
from iolanta.resolvers.python_import import PythonImportResolver


def test_resolver():
    assert PythonImportResolver()[
        URIRef('python://iolanta.facets.generic.BoolLiteral')
    ] == BoolLiteral
