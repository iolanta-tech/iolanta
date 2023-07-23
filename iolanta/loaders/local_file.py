import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, TextIO, Type

from rdflib import Literal, URIRef

from iolanta.conversions import url_to_iri
from iolanta.loaders.base import Loader
from iolanta.loaders.errors import IsAContext, ParserNotFound
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.namespaces import IOLANTA
from iolanta.parsers.base import Parser
from iolanta.parsers.json import JSON
from iolanta.parsers.markdown import Markdown
from iolanta.parsers.yaml import YAML

logger = logging.getLogger(__name__)


def choose_parser_by_extension(path: Path) -> Type[Parser]:
    """
    Choose parser class based on file extension.

    FIXME this is currently hard coded; need to change to a more extensible
      mechanism.
    """
    try:
        return {
            '.json': JSON,
            '.jsonld': JSON,

            '.yaml': YAML,
            '.yamlld': YAML,

            '.md': Markdown,
        }[path.suffix]
    except KeyError:
        raise ParserNotFound(path=path)


@dataclass(frozen=True)
class LocalFile(Loader[Path]):
    """
    Retrieve Linked Data from a file on local disk.

    Requires Path with file:// scheme as input.
    """

    def find_context(self, source: str) -> LDContext:
        return {}

    def choose_parser_class(self, source: Path) -> Type[Parser]:
        return choose_parser_by_extension(source)

    def as_quad_stream(
        self,
        source: Path,
        root_loader: Loader[Path],
        iri: Optional[URIRef] = None,
        context: Optional[LDContext] = None,
    ) -> Iterable[Quad]:
        """Extract a sequence of quads from a local file."""
        if source.stem == 'context':
            raise IsAContext(path=source)

        try:
            parser_class = self.choose_parser_class(source)
        except ParserNotFound:
            return []

        if iri is None:
            iri = url_to_iri(source)

        self.logger.info('Loading data into graph: %s', source)
        with source.open() as text_io:
            yield from parser_class().as_quad_stream(
                raw_data=text_io,
                iri=iri,
                context=context,
                root_loader=root_loader,
            )

            yield Quad(
                iri,
                IOLANTA.fileName,
                Literal(source.name),
                URIRef('https://iolanta.tech/loaders/local-file'),
            )

    def as_file(self, source: Path) -> TextIO:
        """Construct a file-like object."""
        with source.open() as text_io:
            return text_io

    def as_jsonld_document(
        self,
        source: Path,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """As JSON-LD document."""
        parser_class: Type[Parser] = self.choose_parser_class(source)
        with source.open() as text_io:
            document = parser_class().as_jsonld_document(text_io)

        if iri is not None and isinstance(document, dict):
            document.setdefault('@id', str(iri))

        return document
