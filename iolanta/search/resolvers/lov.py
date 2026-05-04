"""Linked Open Vocabularies (LOV) term-search resolver."""

import requests

from iolanta.search.models import SearchHit

ENDPOINT = "https://lov.linkeddata.es/dataset/lov/api/v2/term/search"


class LovResolver:
    """Search LOV for class/property terms.

    Always called by the aggregator. For entity-shaped notions (e.g. proper
    names) LOV legitimately returns zero results — that's the right scope,
    not a failure.
    """

    source_name = "lov"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
        """Return raw candidate hits from the LOV term-search API."""
        response = session.get(
            ENDPOINT,
            params={"q": notion},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            SearchHit(
                uri=entry["uri"][0],
                source=self.source_name,
                description=(entry["comment"][0] if entry.get("comment") else None),
                score=entry.get("score"),
                types=entry.get("type") or [],
            )
            for entry in payload["results"]
        ]
