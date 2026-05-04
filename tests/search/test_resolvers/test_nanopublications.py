"""Test NanopublicationsResolver against a captured SPARQL JSON response."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.nanopublications import NanopublicationsResolver

FIXTURE = (
    Path(__file__).parent.parent / "fixtures" / "nanopub_asimov.sparql-json"
)


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_nanopublications_parses_sparql_json_results():  # noqa: WPS118
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = NanopublicationsResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "nanopublication"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://purl.org/np/RA7Y8x9z-fake-asimov-1",
        source="nanopublication",
        description=None,
        score=12.4,  # noqa: WPS432
        types=[],
    )
    assert hits[1].score == 8.31  # noqa: WPS432, WPS459


def test_nanopublications_handles_zero_hits():
    session = _mock_session(
        {"head": {"vars": ["subj", "score"]}, "results": {"bindings": []}},
    )
    resolver = NanopublicationsResolver()
    assert resolver.search("blargh", session) == []


def test_nanopublications_escapes_quotes_in_notion():  # noqa: WPS118
    """A notion containing a double quote must not break the SPARQL string literal."""
    session = _mock_session({"head": {"vars": []}, "results": {"bindings": []}})
    resolver = NanopublicationsResolver()
    resolver.search('say "hello"', session)

    sent_query = session.get.call_args.kwargs["params"]["query"]  # noqa: WPS219
    # The escaped notion should appear with backslash-escaped quotes
    assert 'say \\"hello\\"' in sent_query  # noqa: WPS342
