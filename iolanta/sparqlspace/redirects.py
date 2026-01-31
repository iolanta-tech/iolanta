import re
from types import MappingProxyType

from rdflib import URIRef

# All entries are (pattern, replacement) strings; pattern may be regex with $ for exact match.
REDIRECTS = MappingProxyType(
    {
        # FIXME This is presently hardcoded; we need to
        #   - either find a way to resolve these URLs automatically,
        #   - or create a repository of those redirects online.
        r"http://purl\.org/vocab/vann/$": "https://vocab.org/vann/vann-vocab-20100607.rdf",
        r"https://purl\.org/dc/elements/1\.1/$": "https://purl.org/dc/terms/",
        r"http://www\.w3\.org/1999/02/22-rdf-syntax-ns#$": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        r"http://www\.w3\.org/2000/01/rdf-schema#$": "http://www.w3.org/2000/01/rdf-schema#",
        r"http://www\.w3\.org/2002/07/owl#$": "http://www.w3.org/2002/07/owl#",
        # Add # fragment to OWL and RDFS when URI has no fragment (pattern $ = no fragment)
        # (fixes bug reported at https://stackoverflow.com/q/78934864/1245471)
        r"http://www\.w3\.org/2002/07/owl$": "http://www.w3.org/2002/07/owl#",
        r"http://www\.w3\.org/2000/01/rdf-schema$": "http://www.w3.org/2000/01/rdf-schema#",
        # Redirect FOAF namespace to GitHub mirror
        r"https?://xmlns\.com/foaf/0\.1/.+": "https://raw.githubusercontent.com/foaf/foaf/refs/heads/master/xmlns.com/htdocs/foaf/0.1/index.rdf",
        r"https://www\.nanopub\.org/nschema$": "https://www.nanopub.net/nschema#",
        r"https://nanopub\.org/nschema$": "https://nanopub.net/nschema#",
        # Convert lexvo.org/id URLs to lexvo.org/data URLs
        r"http://lexvo\.org/id/(.+)": r"http://lexvo.org/data/\1",
        r"https://lexvo\.org/id/(.+)": r"http://lexvo.org/data/\1",
        r"https://www\.lexinfo\.net/(.+)": r"http://www.lexinfo.net/\1",
        # Convert Wikidata https:// to http:// (Wikidata JSON-LD uses http:// URIs)
        r"https://www\.wikidata\.org/entity/(.+)": r"http://www.wikidata.org/entity/\1",
    }
)


def apply_redirect(source: URIRef) -> URIRef:  # noqa: WPS210
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

        if re.match(pattern_str, source_str):
            # Replace any group references in the destination (e.g. \1)
            redirected_uri = re.sub(
                pattern_str,
                destination_str,
                source_str,
            )
            return URIRef(redirected_uri)

    return source
