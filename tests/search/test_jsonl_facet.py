"""Test the SearchResultJsonlFacet."""
from unittest.mock import MagicMock

from rdflib import Literal, URIRef

from iolanta.cli.models import JsonLines
from iolanta.facets.errors import FacetNotFound
from iolanta.facets.search.search_result_jsonl import SearchResultJsonlFacet
from iolanta.namespaces import DATATYPES
from iolanta.search.models import SearchHit


def _make_facet(hits, render_returns=None, render_raises_for=None):
    iolanta_mock = MagicMock()

    def fake_render(node, as_datatype):
        uri = str(node)
        if render_raises_for and uri in render_raises_for:
            raise FacetNotFound(node=node, as_datatype=as_datatype)
        return (render_returns or {}).get(uri, "stub-title")

    iolanta_mock.render.side_effect = fake_render

    facet = SearchResultJsonlFacet.__new__(SearchResultJsonlFacet)
    facet.this = Literal(iter(hits), datatype=DATATYPES["search-result"])
    facet.iolanta = iolanta_mock
    return facet, iolanta_mock


def _hit(uri, source="wikidata"):
    return SearchHit(
        uri=uri,
        source=source,
        description=None,
        score=None,
        types=[],
    )


def test_facet_returns_jsonlines_with_one_dict_per_hit():  # noqa: WPS118
    hits = [
        _hit("https://example.org/a"),  # noqa: WPS226
        _hit("https://example.org/b"),  # noqa: WPS226
    ]
    facet, _ = _make_facet(hits)

    result = facet.show()  # noqa: WPS110

    assert isinstance(result, JsonLines)
    lines = list(result.lines)
    assert len(lines) == 2
    uris = sorted(line["uri"] for line in lines)
    assert uris == ["https://example.org/a", "https://example.org/b"]
    for line in lines:
        assert set(line.keys()) == {"uri", "source", "title", "description", "score", "types"}
        assert isinstance(line["types"], list)


def test_facet_resolves_titles_via_iolanta_render():
    hits = [_hit("https://example.org/a")]
    facet, iolanta_mock = _make_facet(
        hits,
        render_returns={"https://example.org/a": "Example A"},
    )

    lines = list(facet.show().lines)

    assert lines[0]["title"] == "Example A"
    iolanta_mock.render.assert_called_once_with(
        URIRef("https://example.org/a"),
        as_datatype=DATATYPES.title,
    )


def test_facet_yields_null_title_when_render_raises_facet_not_found():  # noqa: WPS118
    hits = [
        _hit("https://example.org/a"),  # noqa: WPS226
        _hit("https://example.org/b"),  # noqa: WPS226
    ]
    facet, _ = _make_facet(
        hits,
        render_raises_for={"https://example.org/a"},
        render_returns={"https://example.org/b": "B-title"},
    )

    by_uri = {line["uri"]: line for line in facet.show().lines}
    assert by_uri["https://example.org/a"]["title"] is None
    assert by_uri["https://example.org/b"]["title"] == "B-title"
