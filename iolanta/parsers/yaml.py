import json
from io import StringIO
from typing import Iterable, Optional, TextIO

import yaml
from rdflib import URIRef

from iolanta.loaders import Loader
from iolanta.models import LDContext, LDDocument, Quad
from iolanta.parsers.json import JSON

try:  # noqa
    from yaml import CSafeLoader as SafeLoader  # noqa
except ImportError:
    from yaml import SafeLoader  # type: ignore   # noqa


class YAML(JSON):
    """Load YAML data."""

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Read YAML content and adapt it to JSON-LD format."""
        return yaml.load(raw_data, Loader=SafeLoader)

    def as_quad_stream(
        self,
        raw_data: TextIO,
        iri: Optional[URIRef],
        context: LDContext,
        root_loader: Loader,
    ) -> Iterable[Quad]:
        """Read YAML-LD data into a quad stream."""
        json_data = self.as_jsonld_document(raw_data)

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
