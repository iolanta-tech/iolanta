from iolanta.iolanta import Iolanta
from iolanta.namespaces import RDF


def test_resolve_variable():
    Iolanta().query(query_text='SELECT * WHERE { $iri ?p ?o }', iri=RDF.type)
