import json
from pathlib import Path
from typing import Optional, Dict

import pyparsing
import rdflib
import requests
from fastapi import FastAPI  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import AnyUrl
from pyld import jsonld
from rdflib.plugins.memory import IOMemory
from rdflib.plugins.sparql import prepareQuery
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
def graph() -> rdflib.ConjunctiveGraph:
    store = IOMemory()

    universe = rdflib.ConjunctiveGraph(store=store)
    universe.bind("iolanta", "https://iolanta.tech/")

    # Parse RDFS
    # rdfs_graph = rdflib.Graph(store=store, identifier=rdflib.RDFS.uri)
    # rdfs_graph.parse(str(STATIC_DIRECTORY / 'rdf-schema.n3'), format='n3')

    # And our additions to it
    # iolanta_rdfs_graph = rdflib.Graph(
    #     store=store,
    #     identifier='https://iolanta.tech/apps/iolanta-rdfs/',
    # )
    # iolanta_rdfs_graph.parse(str(STATIC_DIRECTORY / 'iolanta-rdfs.n3'), format='n3')

    return universe


# Find the default lens for the given IRI
IMPLICIT_LENS_QUERY = '''
PREFIX iolanta: <https://iolanta.tech/>

CONSTRUCT WHERE {
    ?lens iolanta:sparql ?sparql .
    ?lens iolanta:frame ?frame .
    ?iri iolanta:lens ?lens .
}
'''


# Find the default lens for the given IRI
EXPLICIT_LENS_QUERY = '''
PREFIX iolanta: <https://iolanta.tech/>

CONSTRUCT
FROM <http://localhost:8000/iolanta-rdfs.n3>
WHERE {
    ?lens iolanta:sparql ?sparql .
    ?lens iolanta:frame ?frame .
}
'''


def get_bindings(iri: AnyUrl, via: Optional[AnyUrl]) -> Dict[str, rdflib.URIRef]:
    """Construct variable bindings for given IRI and lens (if provided)."""
    bindings = {
        'iri': rdflib.URIRef(iri),
    }

    if via:
        bindings.update(
            lens=rdflib.URIRef(via),
        )

    return bindings


def get_sparql_text(url: AnyUrl) -> str:
    """Download SPARQL text file by its URL."""
    print(url)
    response = requests.get(url)

    if response.status_code == 404:
        raise Exception(f'File with a SPARQL query not found at <{url}>.')

    return response.text


def get_lens_for(iri: AnyUrl, via: AnyUrl) -> models.Lens:
    """Fetch a Lens description for further execution."""
    universe = graph()

    query = prepareQuery(EXPLICIT_LENS_QUERY)

    bindings = get_bindings(
        iri=iri,
        via=via,
    )

    lens_graph = json.loads(universe.query(
        query,
        initBindings=bindings,
    ).serialize(format='json-ld'))

    if not lens_graph:
        raise ValueError(
            f'Lens for IRI {iri} with URL {via} not found. '
            f'Query: {EXPLICIT_LENS_QUERY}'
        )

    frame = {
        '@context': {
            '@vocab': 'https://iolanta.tech/',
            'sparql': {
                '@type': '@id',
                '@container': '@set',
            },
            'frame': {'@type': '@id'},
        },
        '@id': via,
    }

    lens_data = jsonld.frame(
        input_=lens_graph,
        frame=frame,
    )

    try:
        frame = requests.get(lens_data['frame']).json()
    except KeyError as err:
        raise Exception(
            f'Could not obtain the frame URL from: '
            f'{json.dumps(lens_data, indent=2)}',
        ) from err

    return models.Lens(
        frame=frame,
        sparql=list(map(
            get_sparql_text,
            lens_data['sparql']
        ))
    )


def apply_lens(iri: AnyUrl, lens: models.Lens) -> dict:
    """Apply lens to given IRI and get the JSON-LD data."""
    universe = graph()

    result = rdflib.Graph()
    for query in lens.sparql:
        try:
            query_result = universe.query(query)
        except pyparsing.ParseException as err:
            raise ValueError(f'Query:\n{query}\n\nError: {err}')

        result += query_result

    # TODO can serialize() return a dict?
    jsonld_subgraph = json.loads(result.serialize(
        format='json-ld',
    ))

    print(result.serialize(format='n3').decode('utf-8'))

    jsonld_subgraph = jsonld.frame(
        input_=jsonld_subgraph,
        frame=lens.frame,
    )

    return jsonld_subgraph


DEFAULT_LENS_URI_QUERY = '''
PREFIX iolanta: <https://iolanta.tech/>

SELECT ?lens
FROM <http://localhost:8000/iolanta-rdfs.n3>
WHERE {
    $iri iolanta:lens ?lens .
}
'''


def get_default_lens_uri_for(iri: AnyUrl) -> str:
    """Search for a suitable lens for a given URI."""
    candidates = graph().query(DEFAULT_LENS_URI_QUERY, initBindings={
        'iri': rdflib.URIRef(iri),
    })

    urls = list(map(
        lambda singleton: singleton[0].toPython(),
        candidates,
    ))

    return urls[0]


@app.get('/view/')
def view(iri: AnyUrl, via: Optional[AnyUrl] = None):
    """List all known lenses for an IRI."""
    if not via:
        via = get_default_lens_uri_for(iri)

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
