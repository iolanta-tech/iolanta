import dataclasses
import hashlib
from types import MappingProxyType
from typing import Iterable, Optional
from urllib.parse import unquote

from documented import DocumentedError
from rdflib import BNode, Literal, URIRef
from rdflib.term import Node

from iolanta.errors import UnresolvedIRI
from iolanta.models import Quad
from iolanta.namespaces import IOLANTA, META

NORMALIZE_TERMS_MAP = MappingProxyType({
    URIRef(_url := 'https://www.w3.org/2002/07/owl'): URIRef(f'{_url}#'),
    URIRef(_url := 'https://www.w3.org/2000/01/rdf-schema'): URIRef(f'{_url}#'),
})


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
        return URIRef(unquote(term_value))

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


def construct_subgraph_name(subgraph_name: str, graph: URIRef) -> URIRef:
    """
    Construct a proper subgraph name URI from a base name and graph.

    If the subgraph name already starts with the graph URI, return it as is.
    Otherwise, append the name as a fragment to the graph URI.
    """
    if subgraph_name.startswith(str(graph)):
        return URIRef(subgraph_name)

    return URIRef(f'{graph}#{subgraph_name}')


def _parse_quads_per_subgraph(
    raw_quads,
    blank_node_prefix: str,
    graph: URIRef,
    subgraph: URIRef,
) -> Iterable[Quad]:
    for quad in raw_quads:
        try:
            yield Quad(
                subject=parse_term(quad['subject'], blank_node_prefix),
                predicate=parse_term(quad['predicate'], blank_node_prefix),
                object=parse_term(quad['object'], blank_node_prefix),
                graph=subgraph,
            )
        except SpaceInProperty as err:
            raise dataclasses.replace(
                err,
                iri=graph,
            )


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

    subgraph_names = {
        URIRef(subgraph_name): construct_subgraph_name(
            subgraph_name,
            graph=graph,
        )
        for subgraph_name in quads_document.keys()
        if subgraph_name != '@default'
    }
    subgraph_names[graph] = graph

    for subgraph, quads in quads_document.items():
        if subgraph == '@default':
            subgraph = graph   # noqa: WPS440

        else:
            subgraph = URIRef(subgraph)

            yield Quad(
                graph,
                IOLANTA['has-sub-graph'],
                subgraph_names[subgraph],
                META,
            )

        quads = _parse_quads_per_subgraph(
            quads,
            blank_node_prefix=blank_node_prefix,
            graph=subgraph,
            subgraph=subgraph_names[subgraph],
        )

        for quad in quads:   # noqa: WPS526
            yield quad.replace(
                subgraph_names | NORMALIZE_TERMS_MAP | {
                    # To enable nanopub rendering
                    URIRef('http://purl.org/nanopub/temp/np/'): graph,
                },
            ).normalize()


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


@dataclasses.dataclass
class SpaceInProperty(DocumentedError):
    """
    Space in property.

    That impedes JSON-LD parsing.

    Please do not use spaces in property names in JSON or YAML data; use `title`
    or other methods instead.

    Document IRI: {self.iri}
    """

    iri: Optional[URIRef] = None
