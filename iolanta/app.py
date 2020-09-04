import json
from pathlib import Path
from typing import Optional

import rdflib
import requests
from fastapi import FastAPI  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import AnyUrl
from pyld import jsonld
from rdflib import ConjunctiveGraph
from rdflib.plugins.memory import IOMemory
from starlette.requests import Request
from starlette.responses import JSONResponse

from iolanta import models

STATIC_DIRECTORY = Path(__file__).parent.parent / 'static'


app = FastAPI()


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Handle an unhandled exception gracefully."""
    return JSONResponse({'message': str(exc)}, status_code=500)


# @functools.lru_cache()
def graph():
    store = IOMemory()

    universe = ConjunctiveGraph(store=store)
    universe.bind("iolanta", "https://iolanta.tech/")

    # Parse RDFS
    rdfs_graph = rdflib.Graph(store=store, identifier=rdflib.RDFS.uri)
    rdfs_graph.parse(str(STATIC_DIRECTORY / 'rdf-schema.n3'), format='n3')

    # And our additions to it
    iolanta_rdfs_graph = rdflib.Graph(
        store=store,
        identifier='https://iolanta.tech/apps/iolanta-rdfs/',
    )
    iolanta_rdfs_graph.parse(str(STATIC_DIRECTORY / 'iolanta-rdfs.n3'), format='n3')

    return universe


LENS_QUERY = '''
PREFIX iolanta: <https://iolanta.tech/>


SELECT ?lens ?sparql ?frame WHERE {
    <$iri> iolanta:lens ?lens .
    ?lens iolanta:sparql ?sparql .
    ?lens iolanta:frame ?frame .
}
'''


def get_lens_for(iri: AnyUrl, via: Optional[AnyUrl] = None) -> models.Lens:
    """Fetch a Lens description for further execution."""
    universe = graph()

    query = LENS_QUERY.replace('$iri', iri)

    raw_lenses = universe.query(query)

    (lens_ref, sparql_path_ref, frame_path_ref), *etc = raw_lenses

    # TODO we automatically assume this is a URIRef, but it can be just text
    sparql_text = requests.get(str(sparql_path_ref)).text
    frame_content = requests.get(str(frame_path_ref)).json()

    return models.Lens(
        sparql_text=sparql_text,
        frame=frame_content,
    )


def apply_lens(iri: AnyUrl, lens: models.Lens) -> dict:
    """Apply lens to given IRI and get the JSON-LD data."""
    universe = graph()

    subgraph = universe.query(lens.sparql_text)

    # TODO can serialize() return a dict?
    jsonld_subgraph = json.loads(subgraph.serialize(
        format='json-ld',
    ))

    print(subgraph.serialize(format='n3').decode('utf-8'))

    jsonld_subgraph = jsonld.frame(
        input_=jsonld_subgraph,
        frame=lens.frame,
    )

    return jsonld_subgraph


@app.get('/view/')
def view(iri: AnyUrl, via: Optional[AnyUrl] = None):
    """List all known lenses for an IRI."""
    lens = get_lens_for(
        iri=iri,
        via=via,
    )

    return apply_lens(
        iri=iri,
        lens=lens,
    )


app.mount(
    "/",
    StaticFiles(
        directory=str(STATIC_DIRECTORY),
        html=True,
    ),
    name="static",
)
