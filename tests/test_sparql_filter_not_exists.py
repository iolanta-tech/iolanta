"""Regression test: FILTER NOT EXISTS with property path triggers ValueError."""
from pathlib import Path

from rdflib import Namespace, Variable
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


def test_extract_mentioned_urls_filter_includes_wrapped_pattern():
    """FILTER must still expose BGP variables (e.g. `$this`) for URL prefetch."""
    query_text = """
    ASK WHERE {
        $this <http://xmlns.com/foaf/0.1/givenName> ?given_name .
        FILTER (lang(?given_name) = "en")
    }
    """
    algebra = translateQuery(parseQuery(query_text)).algebra
    terms = list(extract_mentioned_urls(algebra))
    assert Variable("this") in terms
