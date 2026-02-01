"""CLI alias test for kglint/json."""

import json
from pathlib import Path

from rdflib import URIRef

from iolanta.cli.main import render_and_return

FIXTURES_DIR = Path(__file__).parent / 'data'


def test_cli_kglint_json():
    """CLI with --as kglint/json returns valid JSON with assertions and labels."""
    path = (FIXTURES_DIR / 'clean.yamlld').resolve()
    node = URIRef(f'file://{path}')
    raw = render_and_return(node=node, as_datatype='kglint/json')
    report = json.loads(raw)
    assert 'assertions' in report
    assert 'labels' in report
    assert isinstance(report['assertions'], list)
    assert isinstance(report['labels'], list)
