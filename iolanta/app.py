import functools
import json
from pathlib import Path
from typing import (
    Optional, Dict, TypedDict, List, MutableMapping, Callable,
    TypeVar,
)

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
from platonic_redis import RedisDBMutableMapping

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

CONSTRUCT {
    ?lens iolanta:sparql ?sparql .
    ?lens iolanta:frame ?frame .
    ?sparql iolanta:from-named ?named_graph .
}
FROM <http://localhost:8000/iolanta-rdfs.n3>
WHERE {
    ?lens iolanta:sparql ?sparql .
    ?lens iolanta:frame ?frame .

    OPTIONAL {
        ?sparql iolanta:from-named ?named_graph .
    }
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


SPARQLQueryFrame = TypedDict('SPARQLQueryFrame', {
    '@id': AnyUrl,
    'from-named': List[AnyUrl],
})


def get_sparql_query(query_frame: SPARQLQueryFrame) -> models.SPARQLQuery:
    """Download SPARQL text file by its URL."""

    return models.SPARQLQuery(
        query=requests.get(query_frame['@id']).text,
        from_named=query_frame['from-named'],
    )


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
            'from-named': {'@type': '@id'},
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
        queries=list(map(
            get_sparql_query,
            lens_data['sparql']
        ))
    )


class NamedGraphByURL(RedisDBMutableMapping):
    """Cache RDF graph files by URL."""


KeyType = TypeVar('KeyType')
ValueType = TypeVar('ValueType')


def memoize(
    mapping: MutableMapping[KeyType, ValueType],
) -> Callable[[KeyType], ValueType]:
    def _decorator(func: Callable[[KeyType], ValueType]):
        @functools.wraps(func)
        def wrapper(key: KeyType) -> ValueType:
            try:
                return mapping[key]

            except KeyError:
                calculated_value = func(key)
                mapping[key] = calculated_value
                return calculated_value

        return wrapper

    return _decorator


@memoize(mapping=RedisDBMutableMapping[str, str]())
def fetch_graph_content_by_url(url: AnyUrl) -> str:
    return requests.get(url).text


def graph_by_query(query: models.SPARQLQuery) -> rdflib.Graph:
    """Compose an RDF dataset and run query against it."""
    rdf_dataset = rdflib.ConjunctiveGraph()

    for named_graph_url in query.from_named:
        named_graph_content = fetch_graph_content_by_url(named_graph_url)

        rdf_dataset.parse(
            data=named_graph_content,
            publicID=named_graph_url,
            format='n3',
        )

    return rdf_dataset.query(query.query)


def apply_lens(iri: AnyUrl, lens: models.Lens) -> dict:
    """Apply lens to given IRI and get the JSON-LD data."""
    result = rdflib.Graph()
    for query in lens.queries:
        result += graph_by_query(query)

    # TODO can serialize() return a dict?
    jsonld_subgraph = json.loads(result.serialize(
        format='json-ld',
    ))

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
