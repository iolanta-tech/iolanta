"""Common protocol for the four search resolvers."""
from typing import Protocol

import requests

from iolanta.search.models import SearchHit


class SearchResolver(Protocol):
    """A single source of search candidates.

    Each resolver hits one upstream HTTP API and parses the response into a
    list of `SearchHit`. Resolvers are stateless and receive the shared
    `requests.Session` from the aggregator.
    """

    source_name: str

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
        """Return raw candidate hits for the given notion."""
        ...
