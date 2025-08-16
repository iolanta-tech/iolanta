from pathlib import Path

from mkdocs_macros.plugin import MacrosPlugin
from rdflib import URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def as_uri(uri: Path | str) -> URIRef:
    """Convert a path or string to a URIRef."""
    match uri:
        case Path() as path:
            return path_to_iri(path)

    uri_type = type(uri)
    raise NotImplementedError(f'{uri} ({uri_type.__name__}) is unknown')


def resolve_datatype_uri(uri: str) -> URIRef:
    """Resolve a datatype URI string to a URIRef."""
    return DATATYPES[uri]


def define_env(env: MacrosPlugin):
    iolanta = Iolanta(project_root=Path(__file__).parent / 'docs')

    def as_filter(uri: str, datatype: str) -> str:
        """Convert URI to specified datatype."""
        return iolanta.render(
            node=as_uri(uri),
            as_datatype=resolve_datatype_uri(datatype),
        )

    env.filters['as'] = as_filter
    env.filters['uri'] = as_uri
    env.variables['docs'] = Path(__file__).parent / 'docs'
