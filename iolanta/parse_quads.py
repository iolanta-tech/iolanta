import dataclasses
import hashlib
from typing import Iterable

from rdflib import BNode, Literal, URIRef
from rdflib.term import Node

from iolanta.errors import UnresolvedIRI
from iolanta.models import Quad
from iolanta.namespaces import IOLANTA, RDF
from iolanta.parsers.errors import SpaceInProperty


def parse_term(   # noqa: C901
    term,
    blank_node_prefix,
) -> Node:
    """Parse N-Quads term into a Quad."""
    if term is None:
        raise SpaceInProperty()

    term_type = term['type']
    term_value = term['value']

    if term_type == 'IRI':
        return URIRef(term_value)

    if term_type == 'literal':
        language = term.get('language')

        if datatype := term.get('datatype'):
            datatype = URIRef(datatype)

        if language and datatype:
            datatype = None

        return Literal(
            term_value,
            datatype=datatype,
            lang=language,
        )

    if term_type == 'blank node':
        return BNode(
            value=term_value.replace('_:', f'{blank_node_prefix}_'),
        )

    raise ValueError(f'Unknown term: {term}')


def parse_quads(
    quads_document,
    graph: URIRef,
    blank_node_prefix: str = '',
) -> Iterable[Quad]:
    """Parse an N-Quads output into a Quads stream."""
    blank_node_prefix = hashlib.md5(  # noqa: S324
        blank_node_prefix.encode(),
    ).hexdigest()
    blank_node_prefix = f'_:{blank_node_prefix}'

    for graph_name, quads in quads_document.items():
        if graph_name == '@default':
            graph_name = graph   # noqa: WPS440

        else:
            graph_name = URIRef(graph_name)

            yield Quad(
                graph,
                IOLANTA['has-sub-graph'],
                graph_name,
                graph,
            )

        for quad in quads:
            try:
                yield Quad(
                    subject=parse_term(quad['subject'], blank_node_prefix),
                    predicate=parse_term(quad['predicate'], blank_node_prefix),
                    object=parse_term(quad['object'], blank_node_prefix),
                    graph=graph_name,
                )
            except SpaceInProperty as err:
                raise dataclasses.replace(
                    err,
                    iri=graph,
                )


def raise_if_term_is_qname(term_value: str):
    """Raise an error if a QName is provided instead of a full IRI."""
    prefix, etc = term_value.split(':', 1)

    if etc.startswith('/'):
        return

    if prefix in {'local', 'templates', 'urn'}:
        return

    raise UnresolvedIRI(
        iri=term_value,
        prefix=prefix,
    )
