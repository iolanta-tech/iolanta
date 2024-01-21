from rdflib import RDF

from iolanta.iolanta import Iolanta


def test_resolve_variable():
    Iolanta().query(query_text='SELECT * WHERE { $iri ?p ?o }', iri=RDF.type)
