"""DBpedia Lookup resolver."""
import requests

from iolanta.search.models import SearchHit

ENDPOINT = "https://lookup.dbpedia.org/api/search"
LIMIT_PER_SOURCE = 10


class DBpediaResolver:
    """Search DBpedia via the Lookup API."""

    source_name = "dbpedia"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
        """Return raw candidate hits from the DBpedia Lookup API."""
        response = session.get(
            ENDPOINT,
            params={
                "query": notion,
                "maxResults": LIMIT_PER_SOURCE,
                "format": "JSON",
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            SearchHit(
                uri=doc["resource"][0],
                source=self.source_name,
                description=doc["comment"][0] if doc.get("comment") else None,
                score=None,
                types=doc.get("type") or [],
            )
            for doc in payload["docs"]
        ]
