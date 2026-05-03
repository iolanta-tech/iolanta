"""Wikidata Reconciliation API resolver."""
import json

import requests

from iolanta.search.models import SearchHit

ENDPOINT = "https://wikidata-reconciliation.wmcloud.org/en/api"
LIMIT_PER_SOURCE = 10
ENTITY_PREFIX = "https://www.wikidata.org/entity/"


class WikidataResolver:
    """Search Wikidata via the OpenRefine reconciliation protocol."""

    source_name = "wikidata"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
        """Return raw candidate hits from the Wikidata reconciliation API."""
        queries = json.dumps({"q0": {"query": notion, "limit": LIMIT_PER_SOURCE}})
        response = session.get(ENDPOINT, params={"queries": queries}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        results = payload["q0"]["result"]
        return [
            SearchHit(
                uri=f"{ENTITY_PREFIX}{entry['id']}",
                source=self.source_name,
                description=entry.get("description"),
                score=entry.get("score"),
                types=[
                    f"{ENTITY_PREFIX}{type_entry['id']}"
                    for type_entry in entry.get("type", [])
                ],
            )
            for entry in results
        ]
