from collections.abc import Callable
from typing import cast

from rdflib import Literal, URIRef
from rdflib.namespace import RDFS
from rdflib.term import Node

from iolanta.facets.textual_graph_triples import is_informative_triple
from iolanta.models import Triple


def test_redundant_literal_title_triple_is_hidden():
    subject = URIRef('https://example.com/UTF-8')
    triple = Triple(
        subject=subject,
        predicate=RDFS.label,
        object=Literal('UTF-8'),
    )

    assert not is_informative_triple(
        triple=triple,
        render_title=cast(Callable[[Node], object], {
            subject: 'UTF-8',
            Literal('UTF-8'): 'UTF-8',
        }.__getitem__),
    )


def test_different_literal_title_triple_is_kept():
    subject = URIRef('https://example.com/UTF-8')
    triple = Triple(
        subject=subject,
        predicate=RDFS.label,
        object=Literal('Unicode UTF-8'),
    )

    assert is_informative_triple(
        triple=triple,
        render_title=cast(Callable[[Node], object], {
            subject: 'UTF-8',
            Literal('Unicode UTF-8'): 'Unicode UTF-8',
        }.__getitem__),
    )


def test_iri_object_triple_is_kept_when_title_matches():
    subject = URIRef('https://example.com/UTF-8')
    object_ = URIRef('https://example.com/encoding/UTF-8')
    triple = Triple(
        subject=subject,
        predicate=RDFS.seeAlso,
        object=object_,
    )

    assert is_informative_triple(
        triple=triple,
        render_title=cast(Callable[[Node], object], {
            subject: 'UTF-8',
            object_: 'UTF-8',
        }.__getitem__),
    )


def test_non_label_redundant_literal_title_triple_is_hidden():
    subject = URIRef('https://example.com/UTF-8')
    triple = Triple(
        subject=subject,
        predicate=RDFS.comment,
        object=Literal('UTF-8'),
    )

    assert not is_informative_triple(
        triple=triple,
        render_title=cast(Callable[[Node], object], {
            subject: 'UTF-8',
            Literal('UTF-8'): 'UTF-8',
        }.__getitem__),
    )
