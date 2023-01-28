from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, TextIO

from rdflib import URIRef
from urlpath import URL

from iolanta.loaders.base import Loader, SourceType
from iolanta.models import LDContext, LDDocument, Quad


@dataclass(frozen=True)
class DataTypeChoiceLoader(Loader[Any]):   # type: ignore
    """Try to load a file via several loaders."""

    loader_by_data_type: Dict[type, Loader[Any]]    # type: ignore

    def choose_parser_class(self, source: SourceType):
        raise ValueError('choose_parser_class')

    def as_file(self, source: SourceType) -> TextIO:
        raise ValueError('as_file')

    def find_context(self, source: SourceType) -> LDContext:
        raise ValueError('find_context')

    def resolve_loader(self, source: Any):   # type: ignore
        """Find loader instance by URL."""
        for source_type, loader in self.loader_by_data_type.items():
            if isinstance(source, source_type):
                return loader

        source_type = type(source)
        raise ValueError(
            f'Cannot find a loader for source: {source} '
            f'of type: {source_type}',
        )

    def as_jsonld_document(
        self,
        source: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """Represent a file as a JSON-LD document."""
        return self.resolve_loader(
            source=source,
        ).as_jsonld_document(
            source=source,
            iri=iri,
        )

    def as_quad_stream(
        self,
        source: str,
        iri: Optional[URIRef],
        root_loader: Optional[Loader[URL]] = None,
        context: Optional[LDContext] = None,
    ) -> Iterable[Quad]:
        """Convert data into a stream of RDF quads."""
        return self.resolve_loader(
            source=source,
        ).as_quad_stream(
            source=source,
            iri=iri,
            root_loader=root_loader or self,
            context=context,
        )
