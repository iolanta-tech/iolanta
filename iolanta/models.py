from typing import Optional, List

import pydantic


class SPARQLQuery(pydantic.BaseModel):
    """SPARQL query text and environment."""

    query: str
    from_named: List[str]


class Lens(pydantic.BaseModel):
    queries: List[SPARQLQuery]

    # We honestly do not know what format the dict will have.
    frame: Optional[dict] = None  # type: ignore


class LensReference(pydantic.BaseModel):
    """Reference to a Lens available for certain object."""

    iri: pydantic.AnyUrl
    label: str
