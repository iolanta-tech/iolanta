"""Test the run_search aggregator."""
import json
import time
from unittest.mock import patch

import requests

from iolanta.search.aggregator import run_search
from iolanta.search.models import SearchHit

_STUB_SLEEP_SECONDS = 0.3
# 4 * 0.3 sequential = 1.2; parallel ~0.3 + slack
_PARALLEL_WALL_CLOCK_BUDGET_SECONDS = 0.9


class _StubResolver:
    def __init__(self, source_name, hits=None, raises=None, sleep=0):
        self.source_name = source_name
        self._hits = hits or []
        self._raises = raises
        self._sleep = sleep

    def search(self, notion, session):
        time.sleep(self._sleep)
        if self._raises is not None:
            raise self._raises
        return self._hits


def _hit(source: str) -> SearchHit:
    return SearchHit(
        uri=f"https://example.org/{source}",
        source=source,
        description=None,
        score=None,
        types=[],
    )


def test_run_search_yields_hits_from_all_resolvers():  # noqa: WPS118
    stubs = (
        _StubResolver("wikidata", hits=[_hit("wikidata")]),  # noqa: WPS226
        _StubResolver("dbpedia", hits=[_hit("dbpedia")]),  # noqa: WPS226
        _StubResolver("nanopublication", hits=[_hit("nanopublication")]),
        _StubResolver("lov", hits=[_hit("lov")]),
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        hits = list(run_search("anything"))

    sources = sorted(hit.source for hit in hits)
    assert sources == ["dbpedia", "lov", "nanopublication", "wikidata"]


def test_run_search_emits_stderr_line_when_resolver_raises(  # noqa: WPS118
    capsys,
):
    stubs = (
        _StubResolver("wikidata", hits=[_hit("wikidata")]),
        _StubResolver("dbpedia", raises=requests.RequestException("kaput")),
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        hits = list(run_search("anything"))

    assert [hit.source for hit in hits] == ["wikidata"]
    err_lines = [
        json.loads(line)
        for line in capsys.readouterr().err.splitlines()
        if line
    ]
    assert {"source": "dbpedia", "error": "kaput"} in err_lines


def test_run_search_runs_resolvers_in_parallel():
    """Total wall time must be ~max(per-resolver sleep), not the sum."""
    stubs = tuple(
        _StubResolver(
            f"src{index}",
            hits=[_hit(f"src{index}")],
            sleep=_STUB_SLEEP_SECONDS,
        )
        for index in range(4)
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        start = time.monotonic()
        list(run_search("anything"))
        elapsed = time.monotonic() - start
    # Sequential would take 4 * 0.3 = 1.2s; parallel ~0.3s (slack).
    assert elapsed < _PARALLEL_WALL_CLOCK_BUDGET_SECONDS  # noqa: WPS459
