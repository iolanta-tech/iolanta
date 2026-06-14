"""Tests for visualization nanopub index discovery."""

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from rdflib import URIRef

from iolanta.discovery import visualization_nanopublications as discovery

FIXTURE = (
    Path(__file__).parent / "fixtures" / "visualization_index.sparql-json"
)


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path):
    discovery.setup_visualization_cache(tmp_path / "cache")
    yield
    asyncio.run(discovery.visualization_cache.delete_match("*"))


def _mock_post_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.ok = True
    response.json.return_value = payload
    return response


def _sample_rows() -> list[discovery.VisualizationIndexRow]:
    return [
        discovery.VisualizationIndexRow(
            nanopub=URIRef("http://purl.org/np/RA-test-nanopub-1"),
            target=URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            created="2026-01-15T10:00:00Z",
        ),
        discovery.VisualizationIndexRow(
            nanopub=URIRef("http://purl.org/np/RA-test-nanopub-1"),
            target=URIRef("http://www.w3.org/2000/01/rdf-schema#"),
            created="2026-01-15T10:00:00Z",
        ),
        discovery.VisualizationIndexRow(
            nanopub=URIRef("http://purl.org/np/RA-test-nanopub-2"),
            target=URIRef("http://xmlns.com/foaf/0.1/"),
            created="2026-01-10T08:00:00Z",
        ),
    ]


def _sample_urls() -> list[str]:
    return [
        "http://purl.org/np/RA-test-nanopub-1",
        "http://purl.org/np/RA-test-nanopub-2",
    ]


def test_parse_index_bindings():
    bindings = json.loads(FIXTURE.read_text())["results"]["bindings"]
    rows = discovery._parse_index_bindings(bindings)

    assert len(rows) == 4
    assert rows[0].nanopub == URIRef("http://purl.org/np/RA-test-nanopub-1")
    assert rows[0].target == URIRef(
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    )
    assert rows[0].created == "2026-01-15T10:00:00Z"


def test_dedupe_rows():
    rows = discovery._dedupe_rows(_sample_rows() + [_sample_rows()[0]])

    assert len(rows) == 3


def test_unique_nanopub_uris():
    uris = discovery._unique_nanopub_uris(_sample_rows())

    assert uris == [
        URIRef("http://purl.org/np/RA-test-nanopub-1"),
        URIRef("http://purl.org/np/RA-test-nanopub-2"),
    ]


def test_nanopub_urls_from_bindings():
    bindings = json.loads(FIXTURE.read_text())["results"]["bindings"]

    assert discovery._nanopub_urls_from_bindings(bindings) == _sample_urls()


def _capture_posted_query(monkeypatch) -> list[str]:
    posted_query: list[str] = []

    def capture_post(*_args, **kwargs):
        posted_query.append(kwargs["data"]["query"])
        return _mock_post_response(
            {"results": {"bindings": []}},
        )

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    return posted_query


def test_index_query_shape(monkeypatch):
    posted_query = _capture_posted_query(monkeypatch)
    discovery.fetch_visualization_index()

    assert len(posted_query) == 1
    query = posted_query[0]
    assert query == discovery.INDEX_QUERY
    assert "GRAPH npa:graph" in query
    assert "dcterms:created" in query
    assert "GRAPH ?provenance" in query
    assert "iolanta:visualizes" in query


def test_fresh_cache_avoids_http(monkeypatch):
    post_count = 0

    def capture_post(*_args, **_kwargs):
        nonlocal post_count
        post_count += 1
        return _mock_post_response(json.loads(FIXTURE.read_text()))

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    urls = discovery.fetch_visualization_index()
    cached_urls = discovery.fetch_visualization_index()

    assert post_count == 1
    assert urls == _sample_urls()
    assert cached_urls == _sample_urls()


def test_expired_cache_refreshes(monkeypatch):
    post_count = 0

    def capture_post(*_args, **_kwargs):
        nonlocal post_count
        post_count += 1
        return _mock_post_response(json.loads(FIXTURE.read_text()))

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    discovery.fetch_visualization_index()
    asyncio.run(
        discovery.visualization_cache.delete(
            f"soft:nanopub_urls:{discovery.DEFAULT_TIMEOUT}",
        ),
    )
    urls = discovery.fetch_visualization_index()

    assert post_count == 2
    assert urls == _sample_urls()


def test_failed_refresh_uses_stale(monkeypatch):
    def capture_post(*_args, **_kwargs):
        return _mock_post_response(json.loads(FIXTURE.read_text()))

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    discovery.fetch_visualization_index()

    def failing_post(*_args, **_kwargs):
        response = MagicMock()
        response.ok = False
        response.status_code = 503
        return response

    monkeypatch.setattr(discovery.requests, "post", failing_post)
    urls = discovery.fetch_visualization_index()

    assert urls == _sample_urls()


def test_failed_refresh_without_cache_returns_empty(monkeypatch):
    def failing_post(*_args, **_kwargs):
        response = MagicMock()
        response.ok = False
        response.status_code = 503
        return response

    monkeypatch.setattr(discovery.requests, "post", failing_post)
    urls = discovery.fetch_visualization_index()

    assert urls == []


def test_without_disk_cache_read_refreshes_and_writes(monkeypatch):
    post_count = 0

    def capture_post(*_args, **_kwargs):
        nonlocal post_count
        post_count += 1
        return _mock_post_response(json.loads(FIXTURE.read_text()))

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    discovery.fetch_visualization_index()
    urls = discovery.fetch_visualization_index(use_disk_cache_read=False)

    assert post_count == 2
    assert urls == _sample_urls()
    discovery.fetch_visualization_index()
    assert post_count == 2


def test_without_disk_cache_read_does_not_use_stale_on_failure(monkeypatch):
    def capture_post(*_args, **_kwargs):
        return _mock_post_response(json.loads(FIXTURE.read_text()))

    monkeypatch.setattr(discovery.requests, "post", capture_post)
    discovery.fetch_visualization_index()

    def failing_post(*_args, **_kwargs):
        response = MagicMock()
        response.ok = False
        response.status_code = 503
        return response

    monkeypatch.setattr(discovery.requests, "post", failing_post)
    urls = discovery.fetch_visualization_index(use_disk_cache_read=False)

    assert urls == []


def test_query_registry_raises_registry_unavailable(monkeypatch):
    def failing_post(*_args, **_kwargs):
        response = MagicMock()
        response.ok = False
        response.status_code = 503
        return response

    monkeypatch.setattr(discovery.requests, "post", failing_post)

    with pytest.raises(discovery.RegistryUnavailable):
        discovery._query_registry(discovery.DEFAULT_TIMEOUT)
