"""Discover ontology visualization nanopublications via the public registry.

Implements the publication-and-discovery side of the ADR
`docs/blog/publish-visualization-information-for-ontologies-on.md`:
ontology publishers (or third parties) sign a nanopublication whose provenance
contains `?assertion iolanta:visualizes <ontology>`, and Iolanta finds those
nanopubs at render time and loads them into the local dataset so the existing
ontology facets pick up the term groups and labels.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import loguru
import requests
from rdflib import URIRef
from requests.exceptions import RequestException

from iolanta.sparqlspace.processor import GlobalSPARQLProcessor

if TYPE_CHECKING:
    from iolanta.iolanta import Iolanta

# The `full` repo is documented by Knowledge Pixels as not scalable long-term
# and will be deprecated medium-term. The forward-compatible replacement is a
# per-type repo (`/repo/type/<hash>`) once a visualization-nanopub type IRI is
# agreed and publishers tag their nanopubs via `npx:hasNanopubType`.
# See: https://github.com/knowledgepixels/nanopub-query
ENDPOINT = "https://query.knowledgepixels.com/repo/full"

DEFAULT_TIMEOUT = 10.0
DISCOVERY_CACHE_SIZE = 512

DISCOVERY_QUERY = """\
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX np:      <http://www.nanopub.org/nschema#>
PREFIX npx:     <http://purl.org/nanopub/x/>
PREFIX npa:     <http://purl.org/nanopub/admin/>
PREFIX iolanta: <https://iolanta.tech/>

SELECT ?nanopub WHERE {
  ?nanopub np:hasAssertion       ?assertion ;
           np:hasProvenance      ?provenance ;
           np:hasPublicationInfo ?pubinfo ;
           npa:hasValidSignatureForPublicKey ?pubkey .

  GRAPH ?provenance { ?assertion iolanta:visualizes <%s> }
  GRAPH ?pubinfo    { ?nanopub  dcterms:created     ?created }

  FILTER NOT EXISTS {
    ?invalidator npx:invalidates ?nanopub ;
                 npa:hasValidSignatureForPublicKey ?invalidator_pubkey .
  }
  FILTER NOT EXISTS {
    ?newer npx:supersedes ?nanopub ;
           npa:hasValidSignatureForPublicKey ?newer_pubkey .
  }
}
ORDER BY DESC(?created)
LIMIT 1
"""


def _fetch_bindings(
    query: str, timeout: float
) -> list[dict[str, dict[str, str]]] | None:
    """Run the discovery SPARQL and return result bindings, or `None` on failure."""
    try:
        response = requests.post(
            ENDPOINT,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=timeout,
        )
    except RequestException as request_error:
        loguru.logger.warning(
            "Visualization-nanopub registry request failed: {error}",
            error=request_error,
        )
        return None

    if not response.ok:
        loguru.logger.warning(
            "Visualization-nanopub registry returned HTTP {status}",
            status=response.status_code,
        )
        return None

    try:
        payload = response.json()
    except ValueError as decode_error:
        loguru.logger.warning(
            "Visualization-nanopub registry returned non-JSON: {error}",
            error=decode_error,
        )
        return None

    return payload.get("results", {}).get("bindings", [])


@functools.lru_cache(maxsize=DISCOVERY_CACHE_SIZE)
def discover(
    ontology_iri: URIRef,
    timeout: float = DEFAULT_TIMEOUT,
) -> URIRef | None:
    """Find the most-recent signed, non-invalidated, non-superseded nanopub.

    Returns the URI of the most-recent signed visualization nanopub whose
    provenance asserts `?assertion iolanta:visualizes <ontology_iri>`, or
    `None` if no such nanopub is found or the registry call fails. "Most
    recent" is decided by `dcterms:created` in the publication-info graph;
    last-writer-wins so different publishers' groupings do not mix. The
    result is cached per process so the registry is not hit on every render.
    """
    bindings = _fetch_bindings(DISCOVERY_QUERY % ontology_iri, timeout)
    if not bindings:
        return None

    nanopub_binding = bindings[0].get("nanopub")
    if nanopub_binding is None:
        return None
    return URIRef(nanopub_binding["value"])


def load_into(iolanta: "Iolanta", ontology_iri: URIRef) -> bool:
    """Discover the latest visualization nanopub for `ontology_iri` and load it.

    The discovered nanopub URI is loaded via the SPARQL processor's `load()`
    path so its assertion graph (carrying `vann:termGroup` and label triples)
    becomes available for `terms.sparql`. Returns `True` if a nanopub was
    loaded.

    NOTE: calling `processor.load()` directly is a deliberate scope-leak. The
    `GlobalSPARQLProcessor` was meant to auto-load URIs returned in query
    bindings (the "Cyberspace" abstraction: queries appear to run against the
    union of all RDF on the Web), but that loop is currently disabled because
    auto-loading every URI in every result was prohibitively slow. Until that
    abstraction is restored without the perf regression, we load explicitly.
    """
    nanopub_uri = discover(ontology_iri)
    if nanopub_uri is None:
        return False

    sparql_processor = GlobalSPARQLProcessor(graph=iolanta.graph)
    sparql_processor.load(nanopub_uri)

    iolanta.logger.info(
        "Loaded visualization nanopub {nanopub} for {iri}",
        nanopub=nanopub_uri,
        iri=ontology_iri,
    )
    return True
