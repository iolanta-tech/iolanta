from dataclasses import dataclass

from rdflib import URIRef


@dataclass
class Location:
    """Unique ID and IRI associated with it."""

    page_id: str
    url: str
    facet_iri: URIRef | None = None
