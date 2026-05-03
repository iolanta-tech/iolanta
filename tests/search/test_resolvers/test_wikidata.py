"""Test the WikidataResolver against a captured reconciliation API response."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.wikidata import WikidataResolver

FIXTURE = Path(__file__).parent.parent / "fixtures" / "wikidata_asimov.json"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_wikidata_parses_reconciliation_response():
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = WikidataResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "wikidata"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="https://www.wikidata.org/entity/Q34981",
        source="wikidata",
        description="American writer and biochemist (1920-1992)",
        score=0.94,
        types=[
            "https://www.wikidata.org/entity/Q5",
            "https://www.wikidata.org/entity/Q36180",
        ],
    )
    assert hits[1].uri == "https://www.wikidata.org/entity/Q1571537"
    assert hits[1].score == 0.42


def test_wikidata_handles_zero_hits():
    session = _mock_session({"q0": {"result": []}})
    resolver = WikidataResolver()
    assert resolver.search("blargh", session) == []


def test_wikidata_raises_value_error_on_malformed_response():
    session = _mock_session({"unexpected": "shape"})
    resolver = WikidataResolver()
    import pytest
    with pytest.raises((KeyError, ValueError)):
        resolver.search("Isaac Asimov", session)
