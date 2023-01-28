from pathlib import Path
from typing import Iterator, TypedDict
from urllib.parse import unquote

from rdflib import URIRef
from urlpath import URL

from iolanta.models import Quad, Triple


def triples_to_quads(
    triples: Iterator[Triple],
    graph: URIRef,
) -> Iterator[Quad]:
    """Convert sequence of triples to sequence of quads."""
    yield from (
        triple.as_quad(graph)
        for triple in triples
    )


Doc = TypedDict(
    'Doc', {
        '__doc__': str,
    },
)


def doc(docstring: str) -> Doc:
    """Document a dataclass field."""
    return {
        '__doc__': docstring,
    }


def construct_metadata_graph_name(iri: URIRef) -> URIRef:
    """Graph to store meta information about the file or directory."""
    return URIRef(f'{iri}/_metadata')


def url_to_iri(url: URL) -> URIRef:
    return URIRef(str(url))


def path_to_url(path: Path) -> URL:
    """Construct a file:// URL."""
    return URL(f'file://{path}')


def path_to_iri(path: Path) -> URIRef:
    """Construct a file:// IRI."""
    return URIRef(f'file://{path}')


def url_to_path(url: URL) -> Path:
    """Convert a file:// URL into a UNIX path."""
    return Path(unquote(url.path))
