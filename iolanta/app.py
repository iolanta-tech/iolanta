import functools
import json
from pathlib import Path

import rdflib
import requests
from fastapi import FastAPI  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import AnyUrl
from pyld import jsonld
from starlette.requests import Request
from starlette.responses import JSONResponse

from iolanta.models import Query, Lens

STATIC_DIRECTORY = Path(__file__).parent.parent / 'static'


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
    universe.parse(str(STATIC_DIRECTORY / 'iolanta-rdfs.n3'), format='n3')
    return universe


def query_graph(query: Query) -> dict:    # type: ignore
    triples = list(graph().query(query.query))
    response_graph = rdflib.Graph()

    for triple in triples:
        response_graph.add(triple)

    context = query.context

    jsonld_data = json.loads(response_graph.serialize(
        format='json-ld',
        context=context,
    ))

    return jsonld_data


@app.post('/sparql')
def sparql(query: Query):
    """Execute a SPARQL query via a POST request."""
    return query_graph(query=query)


def get_lens(url: str) -> Lens:
    with open(STATIC_DIRECTORY / 'lens.sparql', 'r') as lens_query_file:
        lens_query = lens_query_file.read()

    lens_query = lens_query.replace('$iri', url)

    g = graph()
    lenses = list(g.query(lens_query))
    (sparql_path_ref, frame_path_ref), *etc = lenses

    # TODO we automatically assume this is a URIRef, but it can be just text
    sparql_text = requests.get(str(sparql_path_ref)).text
    frame_content = requests.get(str(frame_path_ref)).json()

    return Lens(
        sparql_text=sparql_text,
        frame=frame_content,
    )


def execute_lens(iri: str, via: str) -> dict:  # type: ignore
    g = graph()
    lens = get_lens(url=via)

    subgraph = g.query(lens.sparql_text)

    # TODO can serialize() return a dict?
    jsonld_subgraph = json.loads(subgraph.serialize(
        format='json-ld',
        context={
            '@vocab': 'http://www.w3.org/2000/01/rdf-schema#',
        }
    ))

    jsonld_subgraph = jsonld.frame(jsonld_subgraph, lens.frame)

    return jsonld_subgraph


@app.get('/query')
def query(iri: AnyUrl, via: AnyUrl):
    """Fetch given datum from Semantic Web and represent it via given Lens."""
    return execute_lens(
        iri=iri,
        via=via,
    )


app.mount(
    "/",
    StaticFiles(
        directory=str(STATIC_DIRECTORY),
        html=True,
    ),
    name="static",
)
