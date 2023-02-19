import dataclasses
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path
from typing import Iterable, List, Optional, TextIO, Type

from rdflib import URIRef

from iolanta.context import merge
from iolanta.conversions import path_to_iri
from iolanta.ensure_is_context import NotAContext, ensure_is_context
from iolanta.loaders.base import Loader, SourceType
from iolanta.loaders.local_file import LocalFile
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.namespaces import IOLANTA
from iolanta.parsers.base import Parser


def merge_contexts(*contexts: LDContext) -> LDContext:
    return reduce(
        merge,
        filter(bool, contexts),
        {},
    )


@dataclass(frozen=True)
class LocalDirectory(Loader[Path]):
    """
    Retrieve Linked Data from a file on local disk.

    Requires Path with file:// scheme as input.
    """

    context_filenames: List[str] = field(
        default_factory=lambda: [
            'context.yaml',
            'context.yml',
            'context.json',
        ],
    )

    def find_context(self, source: SourceType) -> LDContext:
        raise ValueError('?!!!???')

    def directory_level_context(self, path: Path) -> Optional[LDContext]:
        for file_name in self.context_filenames:
            if (context_path := path / file_name).is_file():
                document = LocalFile(logger=self.logger).as_jsonld_document(
                    source=context_path,
                )

                if document:
                    try:
                        return ensure_is_context(document)
                    except NotAContext as err:
                        raise dataclasses.replace(
                            err,
                            path=context_path,
                        )
        return None

    def choose_parser_class(self, source: Path) -> Type[Parser]:
        """Choose parser class based on file extension."""
        raise ValueError('This is a directory')

    def as_quad_stream(
        self,
        source: Path,
        iri: Optional[URIRef],
        root_loader: Loader[Path],
        context: Optional[LDContext] = None,
    ) -> Iterable[Quad]:
        """Extract a sequence of quads from a local file."""
        if iri is None:
            iri = path_to_iri(source.absolute())

        if not source.is_dir():
            yield from LocalFile(logger=self.logger).as_quad_stream(
                source=source,
                root_loader=root_loader,
                iri=iri,
                context=context,
            )
            return

        context = merge_contexts(
            context,
            self.directory_level_context(source),
        )

        for child in source.iterdir():
            if not iri.endswith('/'):
                iri = URIRef(f'{iri}/')

            child_iri = URIRef(f'{iri}{child.name}')

            if child.is_dir():
                child_iri += '/'

                yield from LocalDirectory(logger=self.logger).as_quad_stream(
                    source=child,
                    iri=child_iri,
                    root_loader=root_loader,
                    context=context,
                )

            elif child.stem != 'context':
                yield from LocalFile(logger=self.logger).as_quad_stream(
                    source=child,
                    iri=child_iri,
                    root_loader=root_loader,
                    context=context,
                )

            if iri is not None:
                yield Quad(
                    subject=child_iri,
                    predicate=IOLANTA.isChildOf,
                    object=iri,
                    graph=URIRef(
                        'https://iolanta.tech/loaders/local-directory',
                    ),
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
        raise ValueError('This is a directory.')
