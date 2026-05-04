"""Parallel fan-out aggregator that drives the four search resolvers."""
import json
import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

import requests

from iolanta.search.models import SearchHit
from iolanta.search.resolvers import RESOLVERS

PER_SOURCE_TIMEOUT_SECONDS = 10

_RESOLVER_FAILURES = (
    requests.RequestException,
    TimeoutError,
    ValueError,
    KeyError,
)


def run_search(notion: str) -> Iterable[SearchHit]:
    """Yield hits from the four parallel resolvers as they complete.

    Per-resolver failures are written as one-line JSON to stderr and
    skipped; successful resolvers still yield. The aggregator never
    raises — every error becomes either a stderr line (resolver failure)
    or absence of hits.

    Args:
        notion: Free-form query string forwarded to every resolver.

    Yields:
        Each ``SearchHit`` returned by any resolver, in completion order.
    """
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=len(RESOLVERS)) as pool:
            futures = {
                pool.submit(resolver.search, notion, session): resolver
                for resolver in RESOLVERS
            }
            for future in as_completed(futures):
                resolver = futures[future]
                try:
                    yield from future.result(
                        timeout=PER_SOURCE_TIMEOUT_SECONDS,
                    )
                except _RESOLVER_FAILURES as error:
                    _emit_failure(resolver.source_name, error)


def _emit_failure(source: str, error: Exception) -> None:
    """Write one JSONL line per resolver failure to stderr.

    Args:
        source: Symbolic name of the resolver that raised.
        error: Exception instance whose ``str()`` becomes the message.
    """
    sys.stderr.write(
        '{0}\n'.format(
            json.dumps({'source': source, 'error': str(error)}),
        ),
    )
    sys.stderr.flush()
