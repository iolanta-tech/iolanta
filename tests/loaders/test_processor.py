from rdflib import ConjunctiveGraph, URIRef
from yaml_ld.errors import NoLinkedDataFoundInHTML

from iolanta.namespaces import IOLANTA
from iolanta.sparqlspace import processor
from iolanta.sparqlspace.processor import GlobalSPARQLProcessor, Loaded


def test_no_linked_data_html_is_marked_failed_and_not_retried(monkeypatch):
    source = URIRef('https://example.com/no-ld')
    calls = 0

    def fake_load_document(uri):
        nonlocal calls
        calls += 1
        raise NoLinkedDataFoundInHTML('No linked data fragments found in HTML')

    monkeypatch.setattr(processor.yaml_ld, 'load_document', fake_load_document)

    sparql_processor = GlobalSPARQLProcessor(graph=ConjunctiveGraph())

    assert isinstance(sparql_processor.load(source), Loaded)
    assert isinstance(sparql_processor.load(source), processor.Skipped)
    assert calls == 1
    assert sparql_processor._is_loaded(source)
    assert (
        source,
        processor.RDF.type,
        IOLANTA['failed'],
        source,
    ) in sparql_processor.graph
