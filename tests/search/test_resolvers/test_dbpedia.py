"""Test the DBpediaResolver against a captured Lookup response."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.dbpedia import DBpediaResolver

FIXTURE = Path(__file__).parent.parent / "fixtures" / "dbpedia_asimov.json"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_dbpedia_parses_lookup_response():
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = DBpediaResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "dbpedia"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://dbpedia.org/resource/Isaac_Asimov",
        source="dbpedia",
        description="Isaac Asimov was a Russian-born American author and professor of biochemistry at Boston University.",  # noqa: E501
        score=None,
        types=[
            "http://dbpedia.org/ontology/Person",
            "http://dbpedia.org/ontology/Writer",
        ],
    )
    # second hit has no `comment` field — description is None
    assert hits[1].description is None
    assert hits[1].score is None


def test_dbpedia_handles_zero_hits():
    session = _mock_session({"docs": []})
    resolver = DBpediaResolver()
    assert resolver.search("blargh", session) == []


def test_dbpedia_raises_on_malformed_response():
    session = _mock_session({"unexpected": "shape"})
    resolver = DBpediaResolver()
    with pytest.raises((KeyError, ValueError)):
        resolver.search("Isaac Asimov", session)
