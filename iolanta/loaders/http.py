import json
from dataclasses import dataclass, field
from functools import reduce
from io import StringIO
from pathlib import Path
from typing import Iterable, List, Optional, TextIO, Type, Union

from documented import DocumentedError
from rdflib import URIRef
from requests import Response
from urlpath import URL

from iolanta.context import merge
from iolanta.conversions import url_to_iri, url_to_path
from iolanta.loaders.base import Loader
from iolanta.loaders.errors import IsAContext, ParserNotFound
from iolanta.loaders.local_file import choose_parser_by_extension
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.parsers.base import Parser
from iolanta.parsers.json import JSON
from iolanta.parsers.markdown import Markdown
from iolanta.parsers.yaml import YAML


@dataclass(frozen=True)
class HTTP(Loader[URL]):
    """
    Retrieve Linked Data from a file on the Web.
    """

    context: LDContext = field(default_factory=dict)

    def choose_parser_class(self, source: URL, response: Response):
        # FIXME hard code. Make this extensible.
        try:
            return choose_parser_by_extension(source)
        except ParserNotFound:
            content_type = response.headers['Content-Type']

            raise ValueError(f'Content type: {content_type}')

    def as_jsonld_document(
        self,
        source: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        if iri is None:
            iri = url_to_iri(source)

        response = source.get()
        response.raise_for_status()

        # `response.text` doesn't work.
        # Reasoning: https://stackoverflow.com/a/72621231/1245471
        response_as_file = StringIO(response.content.decode('utf-8'))

        parser_class: Type[Parser] = self.choose_parser_class(
            source=source,
            response=response,
        )
        try:
            document = parser_class().as_jsonld_document(response_as_file)
        except Exception:
            raise ValueError(response)

        if iri is not None and isinstance(document, dict):
            document.setdefault('@id', str(iri))

        return document

    def as_file(self, source: URL) -> TextIO:
        raise ValueError('!!!')

    def as_quad_stream(
        self,
        source: URL,
        iri: Optional[URIRef],
        root_loader: 'Loader[URL]',
    ) -> Iterable[Quad]:
        try:
            parser_class = self.choose_parser_class(source)
        except ParserNotFound:
            return []

        if iri is None:
            iri = url_to_iri(source)

        with source.open() as text_io:
            return parser_class().as_quad_stream(
                raw_data=text_io,
                iri=iri,
                context=self.context,
                root_loader=root_loader,
            )

    def find_context(self, source: str) -> LDContext:
        raise ValueError('??!!?')
