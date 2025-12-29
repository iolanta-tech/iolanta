from rdflib import URIRef

from iolanta.sparqlspace.redirects import apply_redirect


def test_apply_redirect():
    assert apply_redirect(
        URIRef('https://nanopub.org/nschema'),
    ) == URIRef('https://nanopub.net/nschema#')


def test_apply_redirect_lexvo():
    """Test that lexvo.org/id URLs are redirected to lexvo.org/data."""
    assert apply_redirect(
        URIRef('http://lexvo.org/id/term/hye/%D5%B6%D6%80%D5%A1%D5%B6%D6%84'),
    ) == URIRef('http://lexvo.org/data/term/hye/%D5%B6%D6%80%D5%A1%D5%B6%D6%84')
