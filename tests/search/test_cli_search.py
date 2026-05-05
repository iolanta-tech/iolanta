"""End-to-end test for `iolanta --search ... --as jsonl`."""
import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from iolanta.cli.main import app
from iolanta.search.models import SearchHit


@pytest.fixture
def runner():
    return CliRunner()


def _hit(source: str, uri: str) -> SearchHit:
    return SearchHit(
        uri=uri,
        source=source,
        description=None,
        score=None,
        types=[],
    )


@patch("iolanta.cli.main.run_search")
def test_search_jsonl_emits_one_line_per_hit(mock_run_search, runner):
    mock_run_search.return_value = iter([
        _hit("wikidata", "https://www.wikidata.org/entity/Q34981"),
        _hit("dbpedia", "http://dbpedia.org/resource/Isaac_Asimov"),
    ])
    with patch(
        "iolanta.facets.search.search_result_jsonl."
        "SearchResultJsonlFacet._render_title",
        return_value="stub-title",
    ):
        result = runner.invoke(app, ["--search", "Isaac Asimov", "--as", "jsonl"])

    assert result.exit_code == 0
    lines = [
        json.loads(line) for line in result.stdout.splitlines() if line.strip()
    ]
    assert len(lines) == 2
    uris = sorted(line["uri"] for line in lines)
    assert uris == [
        "http://dbpedia.org/resource/Isaac_Asimov",
        "https://www.wikidata.org/entity/Q34981",
    ]


@patch("iolanta.cli.main.run_search")
def test_search_without_as_exits_with_error(mock_run_search, runner):
    """Bare `iolanta --search Asimov` (no --as) exits 1 with a clear error."""
    mock_run_search.return_value = iter([
        _hit("wikidata", "https://www.wikidata.org/entity/Q34981"),
    ])
    result = runner.invoke(app, ["--search", "Isaac Asimov"])

    assert result.exit_code == 1
