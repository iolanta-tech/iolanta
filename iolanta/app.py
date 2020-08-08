import functools
import json
from pathlib import Path
from typing import List

import pydantic
import rdflib
from fastapi import FastAPI  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from starlette.requests import Request
from starlette.responses import JSONResponse


def some_function(first: int, second: int) -> int:
    """
    We use this function as an example for some real logic.

    This is how you can write a doctest:

    .. code:: python

        >>> some_function(2, 3)
        5

    Enjoy!
    """
    return first + second


app = FastAPI()


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Handle an unhandled exception gracefully."""
    return JSONResponse({'message': str(exc)}, status_code=500)


@functools.lru_cache()
def graph():
    universe = rdflib.Graph()
    universe.parse('https://www.w3.org/2000/01/rdf-schema#')
    return universe


def query_graph(query: str) -> dict:    # type: ignore
    triples = list(graph().query(query))
    response_graph = rdflib.Graph()

    for triple in triples:
        response_graph.add(triple)

    context = {
        "@vocab": "http://www.w3.org/2000/01/rdf-schema#",
    }

    jsonld_data = json.loads(response_graph.serialize(
        format='json-ld',
        context=context,
    ))

    return jsonld_data


class Query(pydantic.BaseModel):
    # TODO we probably do not need this, do we? Just accept SPARQL body as POST
    query: str


@app.post('/sparql')
def sparql(query: Query):
    """Execute a SPARQL query via a POST request."""
    return query_graph(query=query.query)


STATIC_DIRECTORY = Path(__file__).parent.parent / 'static'

app.mount(
    "/",
    StaticFiles(
        directory=str(STATIC_DIRECTORY),
        html=True,
    ),
    name="static",
)
