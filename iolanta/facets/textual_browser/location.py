from dataclasses import dataclass


@dataclass
class Location:
    """Unique ID and IRI associated with it."""

    page_id: str
    url: str
