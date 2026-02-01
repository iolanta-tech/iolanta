"""Per-fixture tests for kglint assertions."""

import json
from pathlib import Path

import pytest
from rdflib import URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta

KGLINT_JSON = URIRef('https://iolanta.tech/kglint/json')

FIXTURES_DIR = Path(__file__).parent / 'data'


def _iolanta_render_fixture(filename: str) -> dict:
    """Load fixture file, render as kglint/json, return parsed report."""
    path = (FIXTURES_DIR / filename).resolve()
    iolanta = Iolanta()
    iolanta.add(path)
    file_iri = path_to_iri(path)
    raw = iolanta.render(node=file_iri, as_datatype=KGLINT_JSON)
    return json.loads(raw)


def test_literal_looks_like_uri():
    """Fixture triggers literal-looks-like-uri assertion."""
    report = _iolanta_render_fixture('literal_looks_like_uri.yamlld')
    assertions = report['assertions']
    assert len(assertions) >= 1
    codes = [a['code'] for a in assertions]
    assert 'literal-looks-like-uri' in codes


def test_literal_looks_like_qname():
    """Fixture triggers literal-looks-like-qname assertion."""
    report = _iolanta_render_fixture('literal_looks_like_qname.yamlld')
    assertions = report['assertions']
    assert len(assertions) >= 1
    codes = [a['code'] for a in assertions]
    assert 'literal-looks-like-qname' in codes


def test_uri_label_identical():
    """Fixture triggers uri-label-identical assertion."""
    report = _iolanta_render_fixture('uri_label_identical.yamlld')
    assertions = report['assertions']
    assert len(assertions) >= 1
    codes = [a['code'] for a in assertions]
    assert 'uri-label-identical' in codes


def test_blank_label_identical():
    """Fixture triggers blank-label-identical assertion."""
    report = _iolanta_render_fixture('blank_label_identical.yamlld')
    assertions = report['assertions']
    assert len(assertions) >= 1
    codes = [a['code'] for a in assertions]
    assert 'blank-label-identical' in codes


def test_clean_has_no_assertions():
    """Clean fixture has empty assertions list."""
    report = _iolanta_render_fixture('clean.yamlld')
    assert report['assertions'] == []
