import json
from typing import Iterable, Optional, TextIO

from rdflib import URIRef
from urlpath import URL

from iolanta.loaders.base import Loader
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.parsers.base import Parser
from iolanta.parsers.dict_parser import DictParser


class JSON(Parser[TextIO]):
    """Load JSON data."""

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Read JSON content as a JSON-LD document."""
        return json.load(raw_data)

    def as_quad_stream(
        self,
        raw_data: TextIO,
        iri: Optional[URIRef],
        context: LDContext,
        root_loader: Loader[URL],
    ) -> Iterable[Quad]:
        """Read JSON-LD data into a quad stream."""
        document = self.as_jsonld_document(raw_data)

        return DictParser().as_quad_stream(
            raw_data=document,
            iri=iri,
            context=context,
            root_loader=root_loader,
        )
