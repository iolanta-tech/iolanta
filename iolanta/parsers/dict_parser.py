import dataclasses
import itertools
import json
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from documented import DocumentedError
from pyld.jsonld import _resolved_context_cache  # noqa: WPS450
from pyld.jsonld import JsonLdError, expand, flatten, to_rdf  # noqa: WPS347
from rdflib import BNode, URIRef
from yarl import URL

from iolanta.errors import UnresolvedIRI
from iolanta.loaders import Loader
from iolanta.models import LDContext, LDDocument, NotLiteralNode, Quad
from iolanta.namespaces import IOLANTA, LOCAL, RDF
from iolanta.parse_quads import parse_quads
from iolanta.parsers.base import Parser, RawDataType


class DictParser(Parser[LDDocument]):
    """
    Old version of dict parser.

    FIXME: Remove this.
    """

    def as_jsonld_document(self, raw_data: LDDocument) -> LDDocument:
        """Do nothing."""
        return raw_data

    def as_quad_stream(
        self,
        raw_data: RawDataType,
        iri: Optional[NotLiteralNode],
        context: LDContext,
        root_loader: Loader,
    ) -> Iterable[Quad]:
        """Do nonsense."""
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
            document = expand(
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

        document = flatten(document)

        static_quads = [
            Quad(iri, RDF.type, IOLANTA.File, iri),
        ]

        try:
            parsed_quads = list(
                parse_quads(
                    quads_document=to_rdf(document),
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
