"""Discover ontology visualization nanopublications via the public registry.

Implements the publication-and-discovery side of the ADR
`docs/blog/publish-visualization-information-for-ontologies-on.md`:
ontology publishers (or third parties) sign a nanopublication whose provenance
contains `?assertion iolanta:visualizes <ontology>`, and Iolanta finds those
nanopubs at render time and loads them into the local dataset so the existing
ontology facets pick up the term groups and labels.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

import loguru
import requests
from cashews import Cache
from cashews.ttl import ttl_to_seconds
from rdflib import URIRef
from requests.exceptions import RequestException

from iolanta.sparqlspace.processor import (
    GlobalSPARQLProcessor,
    Loaded,
    Skipped,
)

if TYPE_CHECKING:
    from iolanta.iolanta import Iolanta

# The `full` repo is documented by Knowledge Pixels as not scalable long-term
# and will be deprecated medium-term. The forward-compatible replacement is a
# per-type repo (`/repo/type/<hash>`) once a visualization-nanopub type IRI is
# agreed and publishers tag their nanopubs via `npx:hasNanopubType`.
# See: https://github.com/knowledgepixels/nanopub-query
ENDPOINT = "https://query.knowledgepixels.com/repo/full"

DEFAULT_TIMEOUT = 10.0
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "iolanta" / "visualization-index"
SOFT_CACHE_TTL = "1d"
SparqlBinding = dict[str, dict[str, str]]

visualization_cache = Cache()

INDEX_QUERY = """\
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX np:      <http://www.nanopub.org/nschema#>
PREFIX npx:     <http://purl.org/nanopub/x/>
PREFIX npa:     <http://purl.org/nanopub/admin/>
PREFIX iolanta: <https://iolanta.tech/>

SELECT DISTINCT ?nanopub ?target ?created WHERE {
  GRAPH npa:graph {
    ?nanopub np:hasAssertion ?assertion ;
             np:hasProvenance ?provenance ;
             npa:hasValidSignatureForPublicKey ?pubkey ;
             dcterms:created ?created .
  }

  GRAPH ?provenance {
    ?assertion iolanta:visualizes ?target .
  }

  FILTER NOT EXISTS {
    GRAPH npa:graph {
      ?invalidator npx:invalidates ?nanopub ;
                   npa:hasValidSignatureForPublicKey ?invalidator_pubkey .
    }
  }

  FILTER NOT EXISTS {
    GRAPH npa:graph {
      ?newer npx:supersedes ?nanopub ;
             npa:hasValidSignatureForPublicKey ?newer_pubkey .
    }
  }
}
ORDER BY DESC(?created)
"""


class RegistryUnavailable(Exception):
    """The visualization registry could not return index data."""


@dataclass(frozen=True)
class VisualizationIndexRow:
    """One active visualization nanopub entry from the registry index."""

    nanopub: URIRef
    target: URIRef
    created: str


def setup_visualization_cache(directory: Path | None = None) -> None:
    """Configure the disk-backed cashews cache for visualization discovery."""
    cache_directory = directory or DEFAULT_CACHE_DIR
    cache_directory.mkdir(parents=True, exist_ok=True)
    visualization_cache.setup(
        f"disk://?directory={cache_directory}&shards=0",
    )


def _binding_value(binding: SparqlBinding, name: str) -> str | None:
    field = binding.get(name)
    if field is None:
        return None
    return field.get("value")


def _binding_is_complete(binding: SparqlBinding) -> bool:
    return all(
        _binding_value(binding, name) is not None
        for name in ("nanopub", "target", "created")
    )


def _parse_index_bindings(
    bindings: list[SparqlBinding],
) -> list[VisualizationIndexRow]:
    """Parse SPARQL-JSON bindings into index rows, skipping malformed rows."""
    rows: list[VisualizationIndexRow] = []
    for binding in bindings:
        nanopub_value = _binding_value(binding, "nanopub")
        target_value = _binding_value(binding, "target")
        created_value = _binding_value(binding, "created")
        if not _binding_is_complete(binding):
            continue
        rows.append(
            VisualizationIndexRow(
                nanopub=URIRef(nanopub_value),
                target=URIRef(target_value),
                created=created_value,
            ),
        )
    return rows


def _dedupe_rows(
    rows: list[VisualizationIndexRow],
) -> list[VisualizationIndexRow]:
    """Collapse repeated registry rows."""
    seen: set[tuple[str, str, str]] = set()
    deduped: list[VisualizationIndexRow] = []
    for row in rows:
        key = (str(row.nanopub), str(row.target), row.created)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _unique_nanopub_uris(rows: list[VisualizationIndexRow]) -> list[URIRef]:
    """Return unique nanopub URIs, preserving first-seen order."""
    seen: set[str] = set()
    uris: list[URIRef] = []
    for row in rows:
        nanopub_key = str(row.nanopub)
        if nanopub_key in seen:
            continue
        seen.add(nanopub_key)
        uris.append(row.nanopub)
    return uris


def _nanopub_urls_from_bindings(bindings: list[SparqlBinding]) -> list[str]:
    rows = _dedupe_rows(_parse_index_bindings(bindings))
    return [str(uri) for uri in _unique_nanopub_uris(rows)]


def _fetch_bindings(query: str, timeout: float) -> list[SparqlBinding] | None:
    """Run discovery SPARQL; return bindings, or `None` on failure."""
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


def _query_registry(timeout: float) -> list[str]:
    bindings = _fetch_bindings(INDEX_QUERY, timeout)
    if bindings is None:
        raise RegistryUnavailable()
    return _nanopub_urls_from_bindings(bindings)


@visualization_cache.soft(
    ttl=SOFT_CACHE_TTL,
    soft_ttl=SOFT_CACHE_TTL,
    key="nanopub_urls:{timeout}",
)
async def _fetch_nanopub_urls_cached(
    timeout: float = DEFAULT_TIMEOUT,
) -> list[str]:
    return _query_registry(timeout)


def _nanopub_urls_cache_key(timeout: float) -> str:
    return f"soft:nanopub_urls:{timeout}"


async def _store_nanopub_urls_cache(
    timeout: float,
    urls: list[str],
) -> None:
    """Write nanopub URLs to the soft disk cache without reading it."""
    ttl = ttl_to_seconds(SOFT_CACHE_TTL)
    soft_ttl = ttl_to_seconds(SOFT_CACHE_TTL)
    soft_expire_at = datetime.now(timezone.utc) + timedelta(seconds=soft_ttl)
    await visualization_cache.set(
        _nanopub_urls_cache_key(timeout),
        [soft_expire_at, urls],
        expire=ttl,
    )


def _fetch_nanopub_urls(
    timeout: float,
    *,
    use_disk_cache_read: bool,
) -> list[str]:
    if use_disk_cache_read:
        return asyncio.run(_fetch_nanopub_urls_cached(timeout))
    urls = _query_registry(timeout)
    asyncio.run(_store_nanopub_urls_cache(timeout, urls))
    return urls


def _log_registry_unavailable(*, use_disk_cache_read: bool) -> None:
    if use_disk_cache_read:
        loguru.logger.warning(
            "Visualization index refresh failed and no cache is available",
        )
        return
    loguru.logger.warning(
        "Visualization index refresh failed (disk cache read disabled)",
    )


def fetch_visualization_index(
    timeout: float = DEFAULT_TIMEOUT,
    *,
    use_disk_cache_read: bool = True,
) -> list[str]:
    """Return active visualization nanopub URLs, with disk cache when fresh."""
    try:
        return _fetch_nanopub_urls(
            timeout,
            use_disk_cache_read=use_disk_cache_read,
        )
    except RegistryUnavailable:
        _log_registry_unavailable(use_disk_cache_read=use_disk_cache_read)
        return []


def load_visualization_index(
    iolanta: Iolanta,
    nanopub_urls: list[str],
) -> int:
    """Load visualization nanopub URLs into `iolanta.graph`.

    NOTE: calling `processor.load()` directly is a deliberate scope-leak. The
    `GlobalSPARQLProcessor` was meant to auto-load URIs returned in query
    bindings (the "Cyberspace" abstraction: queries appear to run against the
    union of all RDF on the Web), but that loop is currently disabled because
    auto-loading every URI in every result was prohibitively slow. Until that
    abstraction is restored without the perf regression, we load explicitly.
    Nanopub document bytes are HTTP-cached by `yaml-ld` via `requests-cache`.
    """
    sparql_processor = GlobalSPARQLProcessor(graph=iolanta.graph)
    loaded_count = 0
    for nanopub_url in nanopub_urls:
        nanopub_uri = URIRef(nanopub_url)
        try:
            load_result = sparql_processor.load(nanopub_uri)
        except (ValueError, OSError) as load_error:
            iolanta.logger.warning(
                "Failed to load visualization nanopub {nanopub}: {error}",
                nanopub=nanopub_uri,
                error=load_error,
            )
            continue
        if isinstance(load_result, (Loaded, Skipped)):
            loaded_count += 1
            iolanta.logger.info(
                "Loaded visualization nanopub {nanopub}",
                nanopub=nanopub_uri,
            )
    return loaded_count


setup_visualization_cache()
