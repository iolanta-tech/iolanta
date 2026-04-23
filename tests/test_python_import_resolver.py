import pytest
from rdflib import URIRef

from iolanta.resolvers.python_import import PythonImportResolver


def test_resolver():
    with pytest.raises(NotImplementedError):
        PythonImportResolver().resolve(URIRef('pkg:pypi/iolanta#boolean'))
