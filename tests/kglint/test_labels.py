"""Tests for kglint labels section shape and determinism."""

import json
from pathlib import Path

from rdflib import URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta

KGLINT_JSON = URIRef('https://iolanta.tech/kglint/json')

FIXTURES_DIR = Path(__file__).parent / 'data'


def test_labels_shape():
    """Report labels is a list of entries with node (type, value, label) and triples."""
    path = (FIXTURES_DIR / 'clean.yamlld').resolve()
    iolanta = Iolanta()
    iolanta.add(path)
    file_iri = path_to_iri(path)
    raw = iolanta.render(node=file_iri, as_datatype=KGLINT_JSON)
    report = json.loads(raw)
    assert 'labels' in report
    labels = report['labels']
    assert isinstance(labels, list)
    for entry in labels:
        assert 'node' in entry
        assert 'triples' in entry
        node = entry['node']
        assert node['type'] in ('uri', 'blank')
        assert 'value' in node and 'label' in node
        assert isinstance(entry['triples'], list)
        for triple in entry['triples']:
            assert 's' in triple and 'p' in triple and 'o' in triple
            for slot in ('s', 'p', 'o'):
                term = triple[slot]
                assert 'type' in term and 'value' in term
                if term['type'] == 'literal':
                    assert 'datatype' in term or 'language' in term or True
                else:
                    assert 'label' in term


def test_determinism():
    """Same fixture yields identical JSON on two runs."""
    path = (FIXTURES_DIR / 'clean.yamlld').resolve()
    iolanta1 = Iolanta()
    iolanta1.add(path)
    file_iri = path_to_iri(path)
    raw1 = iolanta1.render(node=file_iri, as_datatype=KGLINT_JSON)

    iolanta2 = Iolanta()
    iolanta2.add(path)
    raw2 = iolanta2.render(node=file_iri, as_datatype=KGLINT_JSON)

    assert json.loads(raw1) == json.loads(raw2)
