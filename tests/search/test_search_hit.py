"""Test SearchHit dataclass shape and immutability."""
import pytest

from iolanta.search.models import SearchHit


def test_search_hit_holds_all_fields():
    hit = SearchHit(
        uri="https://www.wikidata.org/entity/Q34981",
        source="wikidata",
        description="American writer and biochemist",
        score=0.94,
        types=["https://www.wikidata.org/entity/Q5"],
    )
    assert hit.uri == "https://www.wikidata.org/entity/Q34981"
    assert hit.source == "wikidata"
    assert hit.description == "American writer and biochemist"
    assert hit.score == 0.94
    assert hit.types == ["https://www.wikidata.org/entity/Q5"]


def test_search_hit_allows_optional_fields_to_be_none_or_empty():
    hit = SearchHit(
        uri="http://purl.org/np/RA7Y",
        source="nanopublication",
        description=None,
        score=12.4,
        types=[],
    )
    assert hit.description is None
    assert hit.types == []


def test_search_hit_is_frozen():
    hit = SearchHit(
        uri="https://example.org/a",
        source="wikidata",
        description=None,
        score=None,
        types=[],
    )
    with pytest.raises((AttributeError, TypeError)):
        hit.uri = "https://example.org/b"  # type: ignore[misc]
