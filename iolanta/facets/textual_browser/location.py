from dataclasses import dataclass

from rdflib import URIRef

from iolanta.models import NotLiteralNode


@dataclass
class Location:
    """Unique ID and IRI associated with it."""

    page_id: str
    url: NotLiteralNode
    facet_iri: URIRef | None = None
