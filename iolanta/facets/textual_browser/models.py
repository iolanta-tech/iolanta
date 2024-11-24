from dataclasses import dataclass

from rdflib import URIRef


@dataclass
class FlipOption:
    """Option to flip to another facet."""

    facet_iri: URIRef
    title: str
