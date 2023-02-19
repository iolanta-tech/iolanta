from abc import ABC
from dataclasses import dataclass
from logging import Logger
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Optional,
    TextIO,
    TypedDict,
    TypeVar,
)

from rdflib import URIRef
from urlpath import URL

from iolanta.conversions import url_to_iri
from iolanta.ensure_is_context import ensure_is_context
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.namespaces import PYTHON

SourceType = TypeVar('SourceType')


PyLDOptions = Dict[str, Any]   # type: ignore

PyLDResponse = TypedDict(
    'PyLDResponse', {
        'contentType': str,
        'contextUrl': Optional[str],
        'documentUrl': str,
        'document': LDDocument,
    },
)


def term_for_python_class(cls: type) -> URIRef:
    """Construct term for Python class."""
    return PYTHON.term(f'{cls.__module__}.{cls.__qualname__}')


# noinspection TaskProblemsInspection
@dataclass(frozen=True)
class Loader(ABC, Generic[SourceType]):
    """
    Base class for loaders.

    Loader receives a URL (or a path) to certain location. It is responsible for
    reading data from that location and returning it as a stream of RDF quads.

    Usually, depending on the data format, Loader leverages Parsers for that
    purpose.
    """

    logger: Logger

    @classmethod
    def loader_class_iri(cls) -> URIRef:
        """Import path to the loader class."""
        return term_for_python_class(cls)

    def choose_parser_class(self, source: SourceType):
        """Find which parser class to use for this URL."""
        raise NotImplementedError(
            f'{self}.choose_parser_class() is not implemented.',
        )

    def as_jsonld_document(
        self,
        source: SourceType,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """Represent a file as a JSON-LD document."""
        raise NotImplementedError(
            f'{self}.as_jsonld_document() is not implemented.',
        )

    def as_file(self, source: SourceType) -> TextIO:
        """Construct a file-like object."""
        raise NotImplementedError()

    def as_quad_stream(
        self,
        source: SourceType,
        iri: Optional[URIRef],
        root_loader: 'Loader[SourceType]',
        context: Optional[LDContext] = None,
    ) -> Iterable[Quad]:
        """Convert data into a stream of RDF quads."""
        raise NotImplementedError(
            f'{self}.as_quad_stream() is not implemented.',
        )

    def find_context(self, source: SourceType) -> LDContext:
        """Find context for the file."""
        raise NotImplementedError(
            f'{self}.find_context() is not implemented.',
        )

    def __call__(self, source: str, options: PyLDOptions) -> PyLDResponse:
        """
        Call the loader to retrieve the document in a PYLD friendly format.

        Used to resolve remote contexts.

        The type of `source` parameter is intentionally `str`: that's the only
        thing which pyld can do.
        """
        source = URL(source)

        document = ensure_is_context(
            self.as_jsonld_document(
                source=URL(source),
                iri=url_to_iri(source),
            ),
        )

        return {
            'document': document,
            'contextUrl': None,
            'documentUrl': source,
            'contentType': 'application/ld+json',
        }
