from rdflib import URIRef

from iolanta.sparqlspace.redirects import apply_redirect


def test_apply_redirect():
    assert apply_redirect(
        URIRef("https://nanopub.org/nschema"),
    ) == URIRef("https://nanopub.net/nschema#")


def test_apply_redirect_dc_elements_https_to_http():
    """DC Elements terms normalize from https:// to canonical http://."""
    assert apply_redirect(
        URIRef("https://purl.org/dc/elements/1.1/title"),
    ) == URIRef("http://purl.org/dc/elements/1.1/title")


def test_apply_redirect_dc_terms_https_to_http():
    """DC Terms IRIs normalize from https:// to canonical http://."""
    assert apply_redirect(
        URIRef("https://purl.org/dc/terms/title"),
    ) == URIRef("http://purl.org/dc/terms/title")


def test_apply_redirect_dc_elements_canonical_stable():
    """Canonical DC Elements `http://` terms are unchanged by redirect."""
    uri = URIRef("http://purl.org/dc/elements/1.1/title")
    assert apply_redirect(uri) == uri


def test_apply_redirect_dc_terms_canonical_stable():
    """Canonical DC Terms `http://` terms are unchanged by redirect."""
    uri = URIRef("http://purl.org/dc/terms/title")
    assert apply_redirect(uri) == uri


def test_apply_redirect_lexvo():
    """Test that lexvo.org/id URLs are redirected to lexvo.org/data."""
    assert apply_redirect(
        URIRef("http://lexvo.org/id/term/hye/%D5%B6%D6%80%D5%A1%D5%B6%D6%84"),
    ) == URIRef("http://lexvo.org/data/term/hye/%D5%B6%D6%80%D5%A1%D5%B6%D6%84")


def test_apply_redirect_wikidata_normalize_hosts():
    """Bare or www Wikidata entity URLs become `http://www.wikidata.org/...`."""
    http_www = URIRef("http://www.wikidata.org/entity/Q188639")
    assert apply_redirect(URIRef("https://wikidata.org/entity/Q188639")) == http_www
    assert apply_redirect(URIRef("https://www.wikidata.org/entity/Q188639")) == http_www


def test_apply_redirect_wikidata_canonical_stable():
    """Canonical `http://www.wikidata.org/entity/...` is unchanged by redirect."""
    uri = URIRef("http://www.wikidata.org/entity/Q188639")
    assert apply_redirect(uri) == uri


def test_apply_redirect_wikidata_http_bare_adds_www():
    """`http://wikidata.org/...` gains `www` host."""
    assert apply_redirect(
        URIRef("http://wikidata.org/entity/Q1"),
    ) == URIRef("http://www.wikidata.org/entity/Q1")
