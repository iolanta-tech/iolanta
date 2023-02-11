from dataclasses import dataclass
from typing import Iterable, Optional, TextIO, Type

from rdflib import Literal, URIRef

from iolanta.conversions import url_to_iri
from iolanta.loaders.base import Loader
from iolanta.loaders.errors import IsAContext, ParserNotFound
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.namespaces import IOLANTA
from iolanta.parsers.base import Parser
from iolanta.parsers.dict_parser import DictParser
from iolanta.parsers.json import JSON
from iolanta.parsers.markdown import Markdown
from iolanta.parsers.yaml import YAML


@dataclass(frozen=True)
class DictLoader(Loader[LDDocument]):
    """
    Retrieve Linked Data from a file on local disk.

    Requires a dict of raw JSON-LD data.
    """

    def find_context(self, source: str) -> LDContext:
        raise ValueError('???WTF?')

    def choose_parser_class(self, source: LDDocument) -> Type[Parser]:
        return DictParser(source)

    def as_quad_stream(
        self,
        source: LDDocument,
        root_loader: Loader[LDDocument],
        iri: Optional[URIRef] = None,
        context: Optional[LDContext] = None,
    ) -> Iterable[Quad]:
        """Extract a sequence of quads."""
        yield from DictParser().as_quad_stream(
            raw_data=source,
            iri=iri,
            context=context,
            root_loader=root_loader,
        )

    def as_file(self, source: LDDocument) -> TextIO:
        """Construct a file-like object."""
        raise ValueError('FOO')

    def as_jsonld_document(
        self,
        source: LDDocument,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """As JSON-LD document."""
        return source
