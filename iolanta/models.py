from typing import Optional

import pydantic


class Query(pydantic.BaseModel):
    # TODO we probably do not need this, do we? Just accept SPARQL body as POST
    query: str
    context: Optional[dict]


class Lens(pydantic.BaseModel):
    sparql_text: str
    frame: Optional[dict] = None
