"""Test that print_renderable streams a JsonLines instance to stdout."""

import json

from iolanta.cli.main import print_renderable
from iolanta.cli.models import JsonLines


def test_print_renderable_streams_jsonlines(capsys):
    payload = JsonLines(
        lines=iter(
            [
                {"uri": "https://example.org/a", "source": "wikidata"},  # noqa: WPS226
                {"uri": "https://example.org/b", "source": "dbpedia"},
            ]
        )
    )

    print_renderable(payload)

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {
        "uri": "https://example.org/a",
        "source": "wikidata",
    }
    assert json.loads(lines[1]) == {"uri": "https://example.org/b", "source": "dbpedia"}
    assert captured.err == ""


def test_print_renderable_jsonlines_unicode(capsys):
    payload = JsonLines(lines=iter([{"title": "Иоланта"}]))

    print_renderable(payload)

    out = capsys.readouterr().out
    # ensure_ascii=False means Cyrillic survives literally, not as \u escapes
    assert "Иоланта" in out
