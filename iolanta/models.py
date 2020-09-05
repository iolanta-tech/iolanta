from typing import Optional, List

import pydantic


class Query(pydantic.BaseModel):
    # TODO we probably do not need this, do we? Just accept SPARQL body as POST
    query: str
    context: Optional[dict]


class Lens(pydantic.BaseModel):
    sparql: List[str]

    # We honestly do not know what format the dict will have.
    frame: Optional[dict] = None  # type: ignore


class LensReference(pydantic.BaseModel):
    """Reference to a Lens available for certain object."""

    iri: pydantic.AnyUrl
    label: str
