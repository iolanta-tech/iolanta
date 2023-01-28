from dataclasses import dataclass
from typing import Optional

from documented import DocumentedError
from rdflib import URIRef


@dataclass
class YAMLError(DocumentedError):
    """
    Invalid YAML.

    File: {self.iri}

    {self.error}
    """

    iri: Optional[URIRef]
    error: Exception


@dataclass
class SpaceInProperty(DocumentedError):
    """
    Space in property.

    That impedes JSON-LD parsing.

    Please do not use spaces in property names in JSON or YAML data; use `title`
    or other methods instead.

    Document IRI: {self.iri}
    """

    iri: Optional[URIRef] = None
