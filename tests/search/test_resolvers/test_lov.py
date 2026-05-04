"""Test LovResolver against captured LOV term-search responses."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.lov import LovResolver

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_lov_parses_term_search_response():
    payload = json.loads((FIXTURES / "lov_author.json").read_text())
    session = _mock_session(payload)
    resolver = LovResolver()

    hits = resolver.search("author of", session)

    assert resolver.source_name == "lov"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://purl.org/dc/terms/creator",
        source="lov",
        description="An entity primarily responsible for making the resource.",
        score=0.91,  # noqa: WPS432
        types=["http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"],
    )
    assert hits[1].description is None  # second entry omits `comment`


def test_lov_zero_hits_for_entity_query():
    """LOV legitimately returns 0 results for entity-shaped queries (e.g. 'Isaac Asimov')."""
    payload = json.loads((FIXTURES / "lov_asimov.json").read_text())
    session = _mock_session(payload)
    resolver = LovResolver()
    assert resolver.search("Isaac Asimov", session) == []
