import json
from io import StringIO
from typing import Iterable, Optional, TextIO

import frontmatter
from rdflib import URIRef
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from iolanta.loaders import Loader
from iolanta.loaders.base import SourceType
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.parsers.errors import YAMLError
from iolanta.parsers.json import JSON
from iolanta.parsers.yaml import YAML

try:  # noqa
    from yaml import CSafeLoader as SafeLoader  # noqa
except ImportError:
    from yaml import SafeLoader  # type: ignore   # noqa


class Markdown(YAML):
    """Load YAML data."""

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Read YAML content and adapt it to JSON-LD format."""
        raw_data.seek(0)
        return frontmatter.load(raw_data).metadata

    def as_quad_stream(
        self,
        raw_data: TextIO,
        iri: Optional[URIRef],
        context: LDContext,
        root_loader: Loader[SourceType],
    ) -> Iterable[Quad]:
        """Assign iolanta:url and generate quad stream."""
        try:
            json_data = self.as_jsonld_document(raw_data)
        except (ScannerError, ParserError) as err:
            raise YAMLError(
                iri=iri,
                error=err,
            ) from err

        return JSON().as_quad_stream(
            raw_data=StringIO(
                json.dumps(
                    json_data,
                    ensure_ascii=False,
                    default=str,
                ),
            ),
            iri=iri,
            context=context,
            root_loader=root_loader,
        )
