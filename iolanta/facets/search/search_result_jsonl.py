"""JSONL facet for search-result Literals."""
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from rdflib import Literal, URIRef

from iolanta.cli.models import JsonLines
from iolanta.facets.cli.base import Renderable, RichFacet
from iolanta.facets.errors import FacetNotFound, NotALiteral
from iolanta.namespaces import DATATYPES
from iolanta.search.models import SearchHit

META = Path(__file__).parent / 'data' / 'search_result.yamlld'

TITLE_RENDER_WORKERS = 8


class SearchResultJsonlFacet(RichFacet):
    """Render a search-result Literal as a stream of JSONL dicts."""

    META = META

    def show(self) -> Renderable:
        """Stream search hits as JSONL records."""
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)
        return JsonLines(lines=self._stream_lines(self.this.value))

    def _stream_lines(
        self,
        hits: Iterable[SearchHit],
    ) -> Iterable[dict]:
        with ThreadPoolExecutor(max_workers=TITLE_RENDER_WORKERS) as pool:
            in_flight = {
                pool.submit(self._render_title, hit.uri): hit for hit in hits
            }
            for future in as_completed(in_flight):
                hit = in_flight[future]
                yield {
                    'uri': hit.uri,
                    'source': hit.source,
                    'title': future.result(),
                    'description': hit.description,
                    'score': hit.score,
                    'types': list(hit.types),
                }

    def _render_title(self, uri: str) -> str | None:
        try:
            return self.iolanta.render(
                URIRef(uri),
                as_datatype=DATATYPES.title,
            )
        except FacetNotFound:
            return None
