from rdflib import URIRef

from iolanta.cyberspace.processor import apply_redirect


def test_apply_redirect():
    assert apply_redirect(
        URIRef('https://nanopub.org/nschema'),
    ) == URIRef('https://nanopub.net/nschema')
