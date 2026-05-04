"""Nanopublications Lucene SAIL resolver."""
import requests

from iolanta.search.models import SearchHit

ENDPOINT = "https://query.knowledgepixels.com/repo/text"
LIMIT_PER_SOURCE = 10

QUERY_TEMPLATE = """\
PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>
SELECT DISTINCT ?subj ?score WHERE {{
  ?subj search:matches [
    search:query "{notion}" ;
    search:score ?score
  ] .
}} ORDER BY DESC(?score) LIMIT {limit}
"""


def _escape_sparql_string(notion: str) -> str:
    """Escape backslashes and double quotes for a SPARQL double-quoted literal."""
    return notion.replace("\\", "\\\\").replace('"', '\\"')  # noqa: WPS342


class NanopublicationsResolver:
    """Search the Nanopublications registry via Lucene SAIL full-text query."""

    source_name = "nanopublication"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
        """Return raw candidate hits from the Nanopublications Lucene SAIL endpoint."""
        query = QUERY_TEMPLATE.format(
            notion=_escape_sparql_string(notion),
            limit=LIMIT_PER_SOURCE,
        )
        response = session.get(
            ENDPOINT,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            SearchHit(
                uri=binding["subj"]["value"],
                source=self.source_name,
                description=None,
                score=float(binding["score"]["value"]),
                types=[],
            )
            for binding in payload["results"]["bindings"]
        ]
