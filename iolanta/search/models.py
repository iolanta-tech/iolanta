"""Data models for the search subsystem."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    """A single candidate URI returned by one of the search resolvers.

    Title is intentionally absent: the JSONL facet resolves human-readable
    titles via `iolanta.render(uri, as_datatype=DATATYPES.title)` rather than
    trusting the per-source label fields.
    """

    uri: str
    source: str
    description: str | None
    score: float | None
    types: list[str]
