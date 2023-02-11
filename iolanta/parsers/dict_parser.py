import dataclasses
import itertools
import json
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from documented import DocumentedError
from pyld import jsonld
from pyld.jsonld import JsonLdError, _resolved_context_cache
from rdflib import RDF, XSD, BNode, Literal, URIRef
from rdflib.term import Node
from urlpath import URL

from iolanta.loaders import Loader
from iolanta.models import LDContext, LDDocument, NotLiteralNode, Quad
from iolanta.namespaces import IOLANTA, LOCAL
from iolanta.parsers.base import Parser, RawDataType
from iolanta.parsers.errors import SpaceInProperty


class DictParser(Parser[LDDocument]):
    def as_jsonld_document(self, raw_data: LDDocument) -> LDDocument:
        return raw_data

    def as_quad_stream(
        self,
        raw_data: RawDataType,
        iri: Optional[NotLiteralNode],
        context: LDContext,
        root_loader: Loader,
    ) -> Iterable[Quad]:
        # This helps avoid weird bugs when loading data.
        _resolved_context_cache.clear()

        document = raw_data

        if iri is None:
            uid = uuid.uuid4().hex
            iri = BNode(f'_:dict:{uid}')

        document = assign_key_if_not_present(
            document=document,
            key='iolanta:subjectOf',
            default_value={
                '$id': str(iri),
            },
        )

        try:
            document = jsonld.expand(
                document,
                options={
                    'expandContext': context,
                    'documentLoader': root_loader,

                    # Explanation:
                    #   https://github.com/digitalbazaar/pyld/issues/143
                    'base': str(LOCAL),
                },
            )
        except (JsonLdError, KeyError, TypeError) as err:
            raise ExpandError(
                message=str(err),
                document=document,
                context=context,
                iri=iri,
                document_loader=root_loader,
            ) from err

        document = jsonld.flatten(document)

        static_quads = [
            Quad(iri, RDF.type, IOLANTA.File, iri),
        ]

        try:
            parsed_quads = list(
                parse_quads(
                    quads_document=jsonld.to_rdf(document),
                    # FIXME:
                    #   title: Can iri be None in a parser?
                    #   description: |
                    #     Does it make sense? If not, just change
                    #     the annotation.
                    graph=iri,  # type: ignore
                    blank_node_prefix=str(iri),
                ),
            )
        except UnresolvedIRI as err:
            raise dataclasses.replace(
                err,
                context=context,
                iri=iri,
            )

        return list(
            itertools.chain(
                parsed_quads,
                static_quads,
            ),
        )


def assign_key_if_not_present(  # type: ignore
    document: LDDocument,
    key: str,
    default_value: Any,
) -> LDDocument:
    """Add key to document if it does not exist yet."""
    if isinstance(document, dict):
        if document.get(key) is None:
            return {
                key: default_value,
                **document,
            }

        return document

    elif isinstance(document, list):
        return [
            assign_key_if_not_present(    # type: ignore
                document=sub_document,
                key=key,
                default_value=default_value,
            )
            for sub_document in document
        ]

    return document


@dataclass
class UnresolvedIRI(DocumentedError):
    """
    An unresolved IRI found.

        IRI: {self.iri}
        file: {self.file}
        prefix: {self.prefix}

    Perhaps you forgot to import appropriate context? For example:

    ```yaml
    "@context":
        - {self.prefix}: https://example.com/{self.prefix}/
    ```

    Context: {self.context}
    """

    iri: str
    prefix: str
    file: Optional[str] = None
    context: Optional[LDContext] = None


def raise_if_term_is_qname(term_value: str):
    """Raise an error if a QName is provided instead of a full IRI."""
    prefix, etc = term_value.split(':', 1)

    if etc.startswith('/'):
        return

    if prefix in {'local', 'templates'}:
        return

    raise UnresolvedIRI(
        iri=term_value,
        prefix=prefix,
    )


def parse_term(
    term,
    blank_node_prefix,
) -> Node:
    """Parse N-Quads term into a Quad."""
    if term is None:
        raise SpaceInProperty()

    term_type = term['type']
    term_value = term['value']

    if term_type == 'IRI':
        raise_if_term_is_qname(term_value)
        return URIRef(term_value)

    if term_type == 'literal':
        language = term.get('language')

        if datatype := term.get('datatype'):
            datatype = URIRef(datatype)

            # XSD.string does not provide any extra information. Removing it.
            if datatype == XSD.string:
                datatype = None

        if language and datatype:
            datatype = None

        return Literal(
            term_value,
            datatype=datatype,
            lang=language,
        )

    if term_type == 'blank node':
        return BNode(
            value=term_value.replace('_:', f'{blank_node_prefix}/'),
        )

    raise ValueError(f'Unknown term: {term}')


def parse_quads(
    quads_document,
    graph: URIRef,
    blank_node_prefix: str = '',
) -> Iterable[Quad]:
    """Parse an N-Quads output into a Quads stream."""
    for graph_name, quads in quads_document.items():
        if graph_name == '@default':
            graph_name = graph

        else:
            graph_name = URIRef(graph_name)

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


@dataclass
class ExpandError(DocumentedError):
    """
    JSON-LD expand operation failed.

    IRI: {self.iri}

    Context: {self.formatted_context}

    Document: {self.formatted_data}

    Error: {self.message}

    Document Loader: {self.document_loader}
    """

    message: str
    document: LDDocument
    context: LDContext
    iri: Optional[URIRef]
    document_loader: Loader[URL]

    @property
    def formatted_data(self) -> str:
        """Format document for printing."""
        return json.dumps(self.document, indent=2, ensure_ascii=False)

    @property
    def formatted_context(self):
        """Format context for printing."""
        return json.dumps(self.context, indent=2, ensure_ascii=False)
