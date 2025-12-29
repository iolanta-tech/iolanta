import re
from types import MappingProxyType

from rdflib import URIRef

from iolanta.namespaces import (
    DC,
    DCTERMS,
    FOAF,
    OWL,
    PROV,
    RDF,
    RDFS,
    VANN,
)

REDIRECTS = MappingProxyType({
    # FIXME This is presently hardcoded; we need to
    #   - either find a way to resolve these URLs automatically,
    #   - or create a repository of those redirects online.
    'http://purl.org/vocab/vann/': URIRef(
        'https://vocab.org/vann/vann-vocab-20100607.rdf',
    ),
    URIRef(str(DC)): URIRef(str(DCTERMS)),
    URIRef(str(RDF)): URIRef(str(RDF)),
    URIRef(str(RDFS)): URIRef(str(RDFS)),
    URIRef(str(OWL)): URIRef(str(OWL)),

    # Add # fragment to OWL and RDFS namespace URIs
    # (fixes bug reported at https://stackoverflow.com/q/78934864/1245471)
    URIRef('http://www.w3.org/2002/07/owl'): URIRef('http://www.w3.org/2002/07/owl#'),
    URIRef('http://www.w3.org/2000/01/rdf-schema'): URIRef('http://www.w3.org/2000/01/rdf-schema#'),

    # Redirect FOAF namespace to GitHub mirror
    URIRef('https?://xmlns.com/foaf/0.1/.+'): URIRef(
        'https://raw.githubusercontent.com/foaf/foaf/refs/heads/master/xmlns.com/htdocs/foaf/0.1/index.rdf',
    ),
    URIRef('https://www.nanopub.org/nschema'): URIRef(
        'https://www.nanopub.net/nschema#',
    ),
    URIRef('https://nanopub.org/nschema'): URIRef(
        'https://nanopub.net/nschema#',
    ),

    # Convert lexvo.org/id URLs to lexvo.org/data URLs
    r'http://lexvo\.org/id/(.+)': r'http://lexvo.org/data/\1',
    r'https://lexvo\.org/id/(.+)': r'http://lexvo.org/data/\1',
    r'https://www\.lexinfo\.net/(.+)': r'http://www.lexinfo.net/\1',
    # Convert Wikidata https:// to http:// (Wikidata JSON-LD uses http:// URIs)
    r'https://www\.wikidata\.org/entity/(.+)': r'http://www.wikidata.org/entity/\1',
})


def apply_redirect(source: URIRef) -> URIRef:   # noqa: WPS210
    """
    Rewrite the URL using regex patterns and group substitutions.

    For each pattern in REDIRECTS:
    - If the pattern matches the source URI
    - Replace the source with the destination, substituting any regex groups
    """
    source_str = str(source)

    for pattern, destination in REDIRECTS.items():
        pattern_str = str(pattern)
        destination_str = str(destination)

        match = re.match(pattern_str, source_str)
        if match:
            # Replace any group references in the destination
            # (like \1, \2, etc.)
            redirected_uri = re.sub(
                pattern_str,
                destination_str,
                source_str,
            )
            return URIRef(redirected_uri)

    return source
