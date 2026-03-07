"""Regression test: FILTER NOT EXISTS with property path triggers ValueError."""
from pathlib import Path

from rdflib import Namespace
from rdflib.namespace import RDF, XSD
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery

from iolanta.sparqlspace.processor import extract_mentioned_urls

SPARQL_FILE = Path(__file__).parent / "tests.sparql"

MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")
JLD = Namespace("https://json-ld.github.io/yaml-ld/tests/vocab#")

NAMESPACES = {
    "mf": MF,
    "rdf": RDF,
    "xsd": XSD,
    "jld": JLD,
}


def test_extract_mentioned_urls_filter_not_exists():
    """FILTER NOT EXISTS with property path must not raise ValueError."""
    query_text = SPARQL_FILE.read_text()
    parsed = parseQuery(query_text)
    algebra = translateQuery(parsed, initNs=NAMESPACES).algebra
    list(extract_mentioned_urls(algebra))
