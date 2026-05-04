"""Search resolvers (one per upstream source)."""
from iolanta.search.resolvers.base import SearchResolver
from iolanta.search.resolvers.dbpedia import DBpediaResolver
from iolanta.search.resolvers.lov import LovResolver
from iolanta.search.resolvers.nanopublications import NanopublicationsResolver
from iolanta.search.resolvers.wikidata import WikidataResolver

RESOLVERS: tuple[SearchResolver, ...] = (
    WikidataResolver(),
    DBpediaResolver(),
    NanopublicationsResolver(),
    LovResolver(),
)

__all__ = ['RESOLVERS', 'SearchResolver']
