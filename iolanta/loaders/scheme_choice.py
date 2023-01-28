from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from rdflib import URIRef
from urlpath import URL

from iolanta.conversions import url_to_iri
from iolanta.ensure_is_context import ensure_is_context
from iolanta.loaders.base import Loader, PyLDOptions, PyLDResponse
from iolanta.models import LDContext, LDDocument, Quad


@dataclass(frozen=True)
class SchemeChoiceLoader(Loader[URL]):
    """Try to load a file via several loaders."""

    loader_by_scheme: Dict[str, Loader[URL]]

    def __call__(self, source: str, options: PyLDOptions) -> PyLDResponse:
        """Compile document for PyLD."""
        source = URL(source)

        document = ensure_is_context(
            self.as_jsonld_document(
                source=source,
                iri=url_to_iri(source),
            ),
        )

        return {
            'document': document,
            'contextUrl': None,
            'contentType': 'application/ld+json',
            'documentUrl': str(source),
        }

    def resolve_loader_by_url(self, url: URL):
        """Find loader instance by URL."""
        try:
            return self.loader_by_scheme[url.scheme]
        except (KeyError, AttributeError):
            raise ValueError(f'Cannot find a loader for URL: {url}')

    def as_jsonld_document(
        self,
        source: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """Represent a file as a JSON-LD document."""
        return self.resolve_loader_by_url(
            url=source,
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
        return self.resolve_loader_by_url(
            url=source,
        ).as_quad_stream(
            source=source,
            iri=iri,
            root_loader=root_loader or self,
            context=context,
        )
