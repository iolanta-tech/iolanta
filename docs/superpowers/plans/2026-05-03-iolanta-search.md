# `iolanta --search` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `iolanta --search "<notion>" --as jsonl` that fans out to four linked-data search APIs in parallel and emits one JSON object per candidate URI on stdout.

**Architecture:** New `iolanta/search/` subpackage with four `requests`-backed resolvers (Wikidata Reconciliation, DBpedia Lookup, Nanopublications Lucene SAIL, LOV term search) coordinated by a `ThreadPoolExecutor`-based aggregator. Results flow through Iolanta's existing render pipeline as a `Literal(iterable, datatype="search-result")` and are rendered by a new `SearchResultJsonlFacet` that returns a `JsonLines` wrapper streamed to stdout by the CLI's `print_renderable`.

**Tech Stack:** Python 3.10+, Typer, rdflib, requests (already a project dep — no new deps), `concurrent.futures.ThreadPoolExecutor`, pytest, mkdocs.

**Spec:** [`../specs/2026-05-03-iolanta-search-design.md`](../specs/2026-05-03-iolanta-search-design.md)

**Issue:** [iolanta-tech/iolanta#412](https://github.com/iolanta-tech/iolanta/issues/412)

**Branch:** `412-implement-iolanta-search-as-jsonl` (already created via `gh issue develop 412 --checkout`)

---

## Conventions for every commit

Per `AGENTS.md` (read it before starting if you haven't):

- **C00:** Commit messages are one line.
- **C01:** Every commit message starts with `#412` (the issue ID — no colon after).
- **C02:** First word after `#412` is capitalized.
- **C03 / C04:** `➕` for additions (don't write "Add"), `🧹` for removals.
- **C05:** Wrap code references in backticks.
- **C07 / C10:** **One commit per file.** When a task changes multiple files, commit each separately with `git add <single-file>` then `git commit`. Never `git add -A` or `git add .`.
- **C08:** Use single-quoted commit messages: `git commit -m '...'`.
- **F12:** After Python edits, run `j fmt && j lint`. Fix lint findings in touched files before committing.

Sample valid commit: `git commit -m '#412 ➕ \`SearchHit\` dataclass'`

---

## File Structure

```
iolanta/
  search/                                        # NEW subpackage
    __init__.py                                  # empty
    models.py                                    # SearchHit dataclass
    aggregator.py                                # run_search() generator
    resolvers/
      __init__.py                                # exports RESOLVERS list
      base.py                                    # SearchResolver Protocol
      wikidata.py                                # WikidataResolver
      dbpedia.py                                 # DBpediaResolver
      nanopublications.py                        # NanopublicationsResolver
      lov.py                                     # LovResolver

  facets/search/                                 # NEW subpackage
    __init__.py                                  # empty
    data/
      search_result.yamlld                       # datatype + facet metadata
    search_result_jsonl.py                       # SearchResultJsonlFacet

  cli/
    main.py                                      # MODIFY — add --search Option, JsonLines case in print_renderable
    models.py                                    # MODIFY — add JsonLines dataclass

docs/datatypes/jsonl.md                          # NEW — output-datatype docs page

pyproject.toml                                   # MODIFY — add `search-result-jsonl-facet` entry-point

jeeves/__init__.py                               # MODIFY — add refresh-search-fixtures task

tests/search/                                    # NEW
  __init__.py
  conftest.py
  fixtures/
    wikidata_asimov.json
    dbpedia_asimov.json
    nanopub_asimov.sparql-json
    lov_author.json
    lov_asimov.json
  test_resolvers/
    __init__.py
    test_wikidata.py
    test_dbpedia.py
    test_nanopublications.py
    test_lov.py
  test_aggregator.py
  test_jsonl_facet.py
  test_cli_search.py
```

---

## Task 1: `JsonLines` dataclass + `print_renderable` extension

**Why first:** trivial leaf type with no dependencies; needed by every downstream task that emits JSONL.

**Files:**
- Modify: `iolanta/cli/models.py`
- Modify: `iolanta/cli/main.py:168-177` (the existing `print_renderable` function)
- Create: `tests/search/__init__.py` (empty file, makes the package importable)
- Create: `tests/search/test_jsonl_print.py`

- [ ] **Step 1: Create the empty test package `__init__.py`**

```bash
mkdir -p tests/search
```

Create `tests/search/__init__.py` with the single line:
```python
# noqa: D104
```

Run: `git add tests/search/__init__.py && git commit -m '#412 ➕ `tests/search/` package'`

- [ ] **Step 2: Write the failing test**

Create `tests/search/test_jsonl_print.py`:

```python
"""Test that print_renderable streams a JsonLines instance to stdout."""
import json

from iolanta.cli.main import print_renderable
from iolanta.cli.models import JsonLines


def test_print_renderable_streams_jsonlines(capsys):
    payload = JsonLines(lines=iter([
        {"uri": "https://example.org/a", "source": "wikidata"},
        {"uri": "https://example.org/b", "source": "dbpedia"},
    ]))

    print_renderable(payload)

    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"uri": "https://example.org/a", "source": "wikidata"}
    assert json.loads(lines[1]) == {"uri": "https://example.org/b", "source": "dbpedia"}
    assert captured.err == ""


def test_print_renderable_jsonlines_unicode_passthrough(capsys):
    payload = JsonLines(lines=iter([{"title": "Иоланта"}]))

    print_renderable(payload)

    out = capsys.readouterr().out
    # ensure_ascii=False means Cyrillic survives literally, not as \u escapes
    assert "Иоланта" in out
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pytest tests/search/test_jsonl_print.py -v`

Expected: `ImportError` because `JsonLines` does not exist in `iolanta.cli.models`.

- [ ] **Step 4: Implement `JsonLines` in `iolanta/cli/models.py`**

Replace the contents of `iolanta/cli/models.py` with:

```python
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class LogLevel(str, Enum):
    """Logging level."""

    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


@dataclass(frozen=True)
class JsonLines:
    """Streamable JSONL output. Each item becomes one line in the rendered output."""

    lines: Iterable[dict]
```

- [ ] **Step 5: Add the `JsonLines` case to `print_renderable` in `iolanta/cli/main.py`**

Two edits to `iolanta/cli/main.py`:

a) Add the import near the top, alongside the existing `from iolanta.cli.models import LogLevel`:

```python
from iolanta.cli.models import JsonLines, LogLevel
```

b) Add a `json` import if not already present (the file imports many things — confirm `import json` is present at the top; if not, add it after `import contextlib`).

c) Replace the body of `print_renderable` (currently at `iolanta/cli/main.py:168-177`) with:

```python
def print_renderable(renderable) -> None:
    match renderable:
        case JsonLines() as jl:
            for line in jl.lines:
                sys.stdout.write(json.dumps(line, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        case Table() as table:
            console.print(table)
        case str() as text:
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
        case unknown:
            console.print(unknown)
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `pytest tests/search/test_jsonl_print.py -v`

Expected: both tests PASS.

- [ ] **Step 7: Format and lint touched files**

Run: `j fmt && j lint`

Fix any lint findings in `iolanta/cli/models.py`, `iolanta/cli/main.py`, `tests/search/test_jsonl_print.py` before continuing. If `j lint` reports unrelated project-wide errors not introduced here, note them but do not fix them silently.

- [ ] **Step 8: Commit each modified/created file separately (per AGENTS.md C10)**

```bash
git add iolanta/cli/models.py
git commit -m '#412 ➕ `JsonLines` dataclass for streamable JSONL output'

git add iolanta/cli/main.py
git commit -m '#412 ➕ `JsonLines` case to `print_renderable`'

git add tests/search/test_jsonl_print.py
git commit -m '#412 ➕ test for `JsonLines` streaming through `print_renderable`'
```

---

## Task 2: `SearchHit` dataclass

**Files:**
- Create: `iolanta/search/__init__.py`
- Create: `iolanta/search/models.py`
- Create: `tests/search/test_search_hit.py`

- [ ] **Step 1: Create the `iolanta/search/` package**

```bash
mkdir -p iolanta/search
```

Create `iolanta/search/__init__.py`:
```python
# noqa: D104
```

Run: `git add iolanta/search/__init__.py && git commit -m '#412 ➕ `iolanta/search/` package'`

- [ ] **Step 2: Write the failing test**

Create `tests/search/test_search_hit.py`:

```python
"""Test SearchHit dataclass shape and immutability."""
import pytest

from iolanta.search.models import SearchHit


def test_search_hit_holds_all_fields():
    hit = SearchHit(
        uri="https://www.wikidata.org/entity/Q34981",
        source="wikidata",
        description="American writer and biochemist",
        score=0.94,
        types=["https://www.wikidata.org/entity/Q5"],
    )
    assert hit.uri == "https://www.wikidata.org/entity/Q34981"
    assert hit.source == "wikidata"
    assert hit.description == "American writer and biochemist"
    assert hit.score == 0.94
    assert hit.types == ["https://www.wikidata.org/entity/Q5"]


def test_search_hit_allows_optional_fields_to_be_none_or_empty():
    hit = SearchHit(
        uri="http://purl.org/np/RA7Y",
        source="nanopublication",
        description=None,
        score=12.4,
        types=[],
    )
    assert hit.description is None
    assert hit.types == []


def test_search_hit_is_frozen():
    hit = SearchHit(
        uri="https://example.org/a",
        source="wikidata",
        description=None,
        score=None,
        types=[],
    )
    with pytest.raises((AttributeError, TypeError)):
        hit.uri = "https://example.org/b"  # type: ignore[misc]
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pytest tests/search/test_search_hit.py -v`

Expected: `ImportError` (no `iolanta.search.models` yet).

- [ ] **Step 4: Implement `SearchHit`**

Create `iolanta/search/models.py`:

```python
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
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/search/test_search_hit.py -v`

Expected: 3 tests PASS.

- [ ] **Step 6: Format, lint, commit each file**

```bash
j fmt && j lint   # fix touched-file findings

git add iolanta/search/models.py
git commit -m '#412 ➕ `SearchHit` dataclass'

git add tests/search/test_search_hit.py
git commit -m '#412 ➕ test for `SearchHit`'
```

---

## Task 3: `SearchResolver` protocol + resolvers package

**Files:**
- Create: `iolanta/search/resolvers/__init__.py`
- Create: `iolanta/search/resolvers/base.py`

No tests for this task on its own — the protocol is verified structurally by each concrete resolver test in Tasks 4–7.

- [ ] **Step 1: Create the resolvers package directory**

```bash
mkdir -p iolanta/search/resolvers
```

- [ ] **Step 2: Create the protocol**

Create `iolanta/search/resolvers/base.py`:

```python
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
```

- [ ] **Step 3: Create the package `__init__.py`** (will be re-edited in Task 8 to populate `RESOLVERS`)

Create `iolanta/search/resolvers/__init__.py`:

```python
"""Search resolvers (one per upstream source)."""
RESOLVERS: tuple = ()  # populated in Task 8 after each resolver is implemented
```

- [ ] **Step 4: Format, lint, commit each file**

```bash
j fmt && j lint

git add iolanta/search/resolvers/base.py
git commit -m '#412 ➕ `SearchResolver` protocol'

git add iolanta/search/resolvers/__init__.py
git commit -m '#412 ➕ `iolanta.search.resolvers` package init'
```

---

## Task 4: Wikidata Reconciliation resolver

**Files:**
- Create: `tests/search/fixtures/wikidata_asimov.json`
- Create: `tests/search/test_resolvers/__init__.py`
- Create: `tests/search/test_resolvers/test_wikidata.py`
- Create: `iolanta/search/resolvers/wikidata.py`

- [ ] **Step 1: Create the test_resolvers package**

```bash
mkdir -p tests/search/test_resolvers tests/search/fixtures
```

Create `tests/search/test_resolvers/__init__.py`:
```python
# noqa: D104
```

- [ ] **Step 2: Create the Wikidata fixture**

Create `tests/search/fixtures/wikidata_asimov.json`:

```json
{
  "q0": {
    "result": [
      {
        "id": "Q34981",
        "name": "Isaac Asimov",
        "description": "American writer and biochemist (1920-1992)",
        "score": 0.94,
        "type": [
          {"id": "Q5", "name": "human"},
          {"id": "Q36180", "name": "writer"}
        ]
      },
      {
        "id": "Q1571537",
        "name": "Isaac Asimov's Science Fiction Magazine",
        "description": "American science fiction magazine",
        "score": 0.42,
        "type": [
          {"id": "Q41298", "name": "magazine"}
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Write the failing test**

Create `tests/search/test_resolvers/test_wikidata.py`:

```python
"""Test the WikidataResolver against a captured reconciliation API response."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.wikidata import WikidataResolver

FIXTURE = Path(__file__).parent.parent / "fixtures" / "wikidata_asimov.json"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_wikidata_parses_reconciliation_response():
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = WikidataResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "wikidata"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="https://www.wikidata.org/entity/Q34981",
        source="wikidata",
        description="American writer and biochemist (1920-1992)",
        score=0.94,
        types=[
            "https://www.wikidata.org/entity/Q5",
            "https://www.wikidata.org/entity/Q36180",
        ],
    )
    assert hits[1].uri == "https://www.wikidata.org/entity/Q1571537"
    assert hits[1].score == 0.42


def test_wikidata_handles_zero_hits():
    session = _mock_session({"q0": {"result": []}})
    resolver = WikidataResolver()
    assert resolver.search("blargh", session) == []


def test_wikidata_raises_value_error_on_malformed_response():
    session = _mock_session({"unexpected": "shape"})
    resolver = WikidataResolver()
    import pytest
    with pytest.raises((KeyError, ValueError)):
        resolver.search("Isaac Asimov", session)
```

- [ ] **Step 4: Run the test to verify it fails**

Run: `pytest tests/search/test_resolvers/test_wikidata.py -v`

Expected: `ImportError` (no `WikidataResolver` yet).

- [ ] **Step 5: Implement `WikidataResolver`**

Create `iolanta/search/resolvers/wikidata.py`:

```python
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
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `pytest tests/search/test_resolvers/test_wikidata.py -v`

Expected: 3 tests PASS.

- [ ] **Step 7: Format, lint, commit each file**

```bash
j fmt && j lint

git add tests/search/test_resolvers/__init__.py
git commit -m '#412 ➕ `tests/search/test_resolvers/` package'

git add tests/search/fixtures/wikidata_asimov.json
git commit -m '#412 ➕ Wikidata reconciliation fixture for `Isaac Asimov`'

git add iolanta/search/resolvers/wikidata.py
git commit -m '#412 ➕ `WikidataResolver`'

git add tests/search/test_resolvers/test_wikidata.py
git commit -m '#412 ➕ test for `WikidataResolver`'
```

---

## Task 5: DBpedia Lookup resolver

**Files:**
- Create: `tests/search/fixtures/dbpedia_asimov.json`
- Create: `tests/search/test_resolvers/test_dbpedia.py`
- Create: `iolanta/search/resolvers/dbpedia.py`

- [ ] **Step 1: Create the DBpedia fixture**

Create `tests/search/fixtures/dbpedia_asimov.json`:

```json
{
  "docs": [
    {
      "resource": ["http://dbpedia.org/resource/Isaac_Asimov"],
      "label": ["Isaac Asimov"],
      "comment": ["Isaac Asimov was a Russian-born American author and professor of biochemistry at Boston University."],
      "type": [
        "http://dbpedia.org/ontology/Person",
        "http://dbpedia.org/ontology/Writer"
      ],
      "refCount": ["3421"]
    },
    {
      "resource": ["http://dbpedia.org/resource/Asimov%27s_Science_Fiction"],
      "label": ["Asimov's Science Fiction"],
      "type": ["http://dbpedia.org/ontology/Magazine"],
      "refCount": ["89"]
    }
  ]
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/search/test_resolvers/test_dbpedia.py`:

```python
"""Test the DBpediaResolver against a captured Lookup response."""
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.dbpedia import DBpediaResolver

FIXTURE = Path(__file__).parent.parent / "fixtures" / "dbpedia_asimov.json"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_dbpedia_parses_lookup_response():
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = DBpediaResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "dbpedia"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://dbpedia.org/resource/Isaac_Asimov",
        source="dbpedia",
        description="Isaac Asimov was a Russian-born American author and professor of biochemistry at Boston University.",
        score=None,
        types=[
            "http://dbpedia.org/ontology/Person",
            "http://dbpedia.org/ontology/Writer",
        ],
    )
    # second hit has no `comment` field — description is None
    assert hits[1].description is None
    assert hits[1].score is None


def test_dbpedia_handles_zero_hits():
    session = _mock_session({"docs": []})
    resolver = DBpediaResolver()
    assert resolver.search("blargh", session) == []


def test_dbpedia_raises_on_malformed_response():
    session = _mock_session({"unexpected": "shape"})
    resolver = DBpediaResolver()
    with pytest.raises((KeyError, ValueError)):
        resolver.search("Isaac Asimov", session)
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pytest tests/search/test_resolvers/test_dbpedia.py -v`

Expected: `ImportError` (no `DBpediaResolver` yet).

- [ ] **Step 4: Implement `DBpediaResolver`**

Create `iolanta/search/resolvers/dbpedia.py`:

```python
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
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/search/test_resolvers/test_dbpedia.py -v`

Expected: 3 tests PASS.

- [ ] **Step 6: Format, lint, commit each file**

```bash
j fmt && j lint

git add tests/search/fixtures/dbpedia_asimov.json
git commit -m '#412 ➕ DBpedia Lookup fixture for `Isaac Asimov`'

git add iolanta/search/resolvers/dbpedia.py
git commit -m '#412 ➕ `DBpediaResolver`'

git add tests/search/test_resolvers/test_dbpedia.py
git commit -m '#412 ➕ test for `DBpediaResolver`'
```

---

## Task 6: Nanopublications (Lucene SAIL) resolver

**Files:**
- Create: `tests/search/fixtures/nanopub_asimov.sparql-json`
- Create: `tests/search/test_resolvers/test_nanopublications.py`
- Create: `iolanta/search/resolvers/nanopublications.py`

- [ ] **Step 1: Create the nanopub fixture**

Create `tests/search/fixtures/nanopub_asimov.sparql-json`:

```json
{
  "head": {"vars": ["subj", "score"]},
  "results": {
    "bindings": [
      {
        "subj": {"type": "uri", "value": "http://purl.org/np/RA7Y8x9z-fake-asimov-1"},
        "score": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#float", "value": "12.4"}
      },
      {
        "subj": {"type": "uri", "value": "http://purl.org/np/RA7Y8x9z-fake-asimov-2"},
        "score": {"type": "literal", "datatype": "http://www.w3.org/2001/XMLSchema#float", "value": "8.31"}
      }
    ]
  }
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/search/test_resolvers/test_nanopublications.py`:

```python
"""Test NanopublicationsResolver against a captured SPARQL JSON response."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.nanopublications import (
    NanopublicationsResolver,
)

FIXTURE = (
    Path(__file__).parent.parent / "fixtures" / "nanopub_asimov.sparql-json"
)


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_nanopublications_parses_sparql_json_results():
    session = _mock_session(json.loads(FIXTURE.read_text()))
    resolver = NanopublicationsResolver()

    hits = resolver.search("Isaac Asimov", session)

    assert resolver.source_name == "nanopublication"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://purl.org/np/RA7Y8x9z-fake-asimov-1",
        source="nanopublication",
        description=None,
        score=12.4,
        types=[],
    )
    assert hits[1].score == 8.31


def test_nanopublications_handles_zero_hits():
    session = _mock_session({"head": {"vars": ["subj", "score"]}, "results": {"bindings": []}})
    resolver = NanopublicationsResolver()
    assert resolver.search("blargh", session) == []


def test_nanopublications_escapes_quotes_in_notion():
    """A notion containing a double quote must not break the SPARQL string literal."""
    session = _mock_session({"head": {"vars": []}, "results": {"bindings": []}})
    resolver = NanopublicationsResolver()
    resolver.search('say "hello"', session)

    sent_query = session.get.call_args.kwargs["params"]["query"]
    # The escaped notion should appear with backslash-escaped quotes
    assert 'say \\"hello\\"' in sent_query
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pytest tests/search/test_resolvers/test_nanopublications.py -v`

Expected: `ImportError` (no `NanopublicationsResolver` yet).

- [ ] **Step 4: Implement `NanopublicationsResolver`**

Create `iolanta/search/resolvers/nanopublications.py`:

```python
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
    return notion.replace("\\", "\\\\").replace('"', '\\"')


class NanopublicationsResolver:
    """Search the Nanopublications registry via Lucene SAIL full-text query."""

    source_name = "nanopublication"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
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
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/search/test_resolvers/test_nanopublications.py -v`

Expected: 3 tests PASS.

- [ ] **Step 6: Format, lint, commit each file**

```bash
j fmt && j lint

git add tests/search/fixtures/nanopub_asimov.sparql-json
git commit -m '#412 ➕ Nanopub SPARQL JSON fixture for `Isaac Asimov`'

git add iolanta/search/resolvers/nanopublications.py
git commit -m '#412 ➕ `NanopublicationsResolver`'

git add tests/search/test_resolvers/test_nanopublications.py
git commit -m '#412 ➕ test for `NanopublicationsResolver`'
```

---

## Task 7: LOV term-search resolver

**Files:**
- Create: `tests/search/fixtures/lov_author.json`
- Create: `tests/search/fixtures/lov_asimov.json`
- Create: `tests/search/test_resolvers/test_lov.py`
- Create: `iolanta/search/resolvers/lov.py`

- [ ] **Step 1: Create the LOV fixtures**

Create `tests/search/fixtures/lov_author.json` (representative response for a vocabulary term):

```json
{
  "results": [
    {
      "uri": ["http://purl.org/dc/terms/creator"],
      "score": 0.91,
      "type": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"],
      "vocabulary.prefix": ["dct"],
      "comment": ["An entity primarily responsible for making the resource."]
    },
    {
      "uri": ["http://schema.org/author"],
      "score": 0.74,
      "type": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"],
      "vocabulary.prefix": ["schema"]
    }
  ]
}
```

Create `tests/search/fixtures/lov_asimov.json` (zero-hits case for an entity-shaped query — the spec calls this out as "the right scope, not a failure"):

```json
{
  "results": []
}
```

- [ ] **Step 2: Write the failing test**

Create `tests/search/test_resolvers/test_lov.py`:

```python
"""Test LovResolver against captured LOV term-search responses."""
import json
from pathlib import Path
from unittest.mock import MagicMock

from iolanta.search.models import SearchHit
from iolanta.search.resolvers.lov import LovResolver

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _mock_session(payload: dict) -> MagicMock:
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    return session


def test_lov_parses_term_search_response():
    payload = json.loads((FIXTURES / "lov_author.json").read_text())
    session = _mock_session(payload)
    resolver = LovResolver()

    hits = resolver.search("author of", session)

    assert resolver.source_name == "lov"
    assert len(hits) == 2
    assert hits[0] == SearchHit(
        uri="http://purl.org/dc/terms/creator",
        source="lov",
        description="An entity primarily responsible for making the resource.",
        score=0.91,
        types=["http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"],
    )
    assert hits[1].description is None  # second entry omits `comment`


def test_lov_zero_hits_for_entity_query():
    """LOV legitimately returns 0 results for entity-shaped queries (e.g. 'Isaac Asimov')."""
    payload = json.loads((FIXTURES / "lov_asimov.json").read_text())
    session = _mock_session(payload)
    resolver = LovResolver()
    assert resolver.search("Isaac Asimov", session) == []
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pytest tests/search/test_resolvers/test_lov.py -v`

Expected: `ImportError`.

- [ ] **Step 4: Implement `LovResolver`**

Create `iolanta/search/resolvers/lov.py`:

```python
"""Linked Open Vocabularies (LOV) term-search resolver."""
import requests

from iolanta.search.models import SearchHit

ENDPOINT = "https://lov.linkeddata.es/dataset/lov/api/v2/term/search"


class LovResolver:
    """Search LOV for class/property terms.

    Always called by the aggregator. For entity-shaped notions (e.g. proper names)
    LOV legitimately returns zero results — that's the right scope, not a failure.
    """

    source_name = "lov"

    def search(
        self,
        notion: str,
        session: requests.Session,
    ) -> list[SearchHit]:
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
                description=(
                    entry["comment"][0] if entry.get("comment") else None
                ),
                score=entry.get("score"),
                types=entry.get("type") or [],
            )
            for entry in payload["results"]
        ]
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `pytest tests/search/test_resolvers/test_lov.py -v`

Expected: 2 tests PASS.

- [ ] **Step 6: Format, lint, commit each file**

```bash
j fmt && j lint

git add tests/search/fixtures/lov_author.json
git commit -m '#412 ➕ LOV term-search fixture for `author of`'

git add tests/search/fixtures/lov_asimov.json
git commit -m '#412 ➕ LOV zero-hits fixture for entity query'

git add iolanta/search/resolvers/lov.py
git commit -m '#412 ➕ `LovResolver`'

git add tests/search/test_resolvers/test_lov.py
git commit -m '#412 ➕ test for `LovResolver`'
```

---

## Task 8: Wire resolvers into `RESOLVERS` tuple

**Files:**
- Modify: `iolanta/search/resolvers/__init__.py`

- [ ] **Step 1: Replace the placeholder `RESOLVERS` with the populated tuple**

Replace the contents of `iolanta/search/resolvers/__init__.py` with:

```python
"""Search resolvers (one per upstream source)."""
from iolanta.search.resolvers.base import SearchResolver
from iolanta.search.resolvers.dbpedia import DBpediaResolver
from iolanta.search.resolvers.lov import LovResolver
from iolanta.search.resolvers.nanopublications import (
    NanopublicationsResolver,
)
from iolanta.search.resolvers.wikidata import WikidataResolver

RESOLVERS: tuple[SearchResolver, ...] = (
    WikidataResolver(),
    DBpediaResolver(),
    NanopublicationsResolver(),
    LovResolver(),
)

__all__ = ["RESOLVERS", "SearchResolver"]
```

- [ ] **Step 2: Smoke-check the import**

Run: `python -c "from iolanta.search.resolvers import RESOLVERS; print([r.source_name for r in RESOLVERS])"`

Expected output: `['wikidata', 'dbpedia', 'nanopublication', 'lov']`

- [ ] **Step 3: Format, lint, commit**

```bash
j fmt && j lint

git add iolanta/search/resolvers/__init__.py
git commit -m '#412 Populate `RESOLVERS` tuple with all four resolvers'
```

---

## Task 9: Aggregator (`run_search`)

**Files:**
- Create: `tests/search/test_aggregator.py`
- Create: `iolanta/search/aggregator.py`

- [ ] **Step 1: Write the failing test**

Create `tests/search/test_aggregator.py`:

```python
"""Test the run_search aggregator."""
import json
import time
from unittest.mock import patch

import pytest
import requests

from iolanta.search.aggregator import run_search
from iolanta.search.models import SearchHit


class _StubResolver:
    def __init__(self, source_name, hits=None, raises=None, sleep=0.0):
        self.source_name = source_name
        self._hits = hits or []
        self._raises = raises
        self._sleep = sleep

    def search(self, notion, session):
        time.sleep(self._sleep)
        if self._raises is not None:
            raise self._raises
        return self._hits


def _hit(source: str) -> SearchHit:
    return SearchHit(
        uri=f"https://example.org/{source}",
        source=source,
        description=None,
        score=None,
        types=[],
    )


def test_run_search_yields_hits_from_all_resolvers():
    stubs = (
        _StubResolver("wikidata", hits=[_hit("wikidata")]),
        _StubResolver("dbpedia", hits=[_hit("dbpedia")]),
        _StubResolver("nanopublication", hits=[_hit("nanopublication")]),
        _StubResolver("lov", hits=[_hit("lov")]),
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        results = list(run_search("anything"))

    sources = sorted(hit.source for hit in results)
    assert sources == ["dbpedia", "lov", "nanopublication", "wikidata"]


def test_run_search_emits_stderr_line_when_resolver_raises(capsys):
    stubs = (
        _StubResolver("wikidata", hits=[_hit("wikidata")]),
        _StubResolver("dbpedia", raises=requests.RequestException("kaput")),
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        results = list(run_search("anything"))

    assert [hit.source for hit in results] == ["wikidata"]
    err_lines = [
        json.loads(line) for line in capsys.readouterr().err.splitlines() if line
    ]
    assert {"source": "dbpedia", "error": "kaput"} in err_lines


def test_run_search_runs_resolvers_in_parallel():
    """Total wall time must be ~max(per-resolver sleep), not the sum."""
    stubs = tuple(
        _StubResolver(f"src{i}", hits=[_hit(f"src{i}")], sleep=0.3)
        for i in range(4)
    )
    with patch("iolanta.search.aggregator.RESOLVERS", stubs):
        start = time.monotonic()
        list(run_search("anything"))
        elapsed = time.monotonic() - start
    # Sequential would take 4 * 0.3 = 1.2s; parallel ~0.3s (allow generous slack).
    assert elapsed < 0.9
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/search/test_aggregator.py -v`

Expected: `ImportError` (no `iolanta.search.aggregator` yet).

- [ ] **Step 3: Implement `run_search`**

Create `iolanta/search/aggregator.py`:

```python
"""Parallel fan-out aggregator that drives the four search resolvers."""
import json
import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

import requests

from iolanta.search.models import SearchHit
from iolanta.search.resolvers import RESOLVERS

PER_SOURCE_TIMEOUT_SECONDS = 10


def run_search(notion: str) -> Iterable[SearchHit]:
    """Yield hits from the four parallel resolvers as they complete.

    Per-resolver failures are written as one-line JSON to stderr and skipped;
    successful resolvers still yield. The aggregator never raises — every error
    becomes either a stderr line (resolver failure) or absence of hits.
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
                    yield from future.result(timeout=PER_SOURCE_TIMEOUT_SECONDS)
                except (
                    requests.RequestException,
                    TimeoutError,
                    ValueError,
                    KeyError,
                ) as error:
                    print(
                        json.dumps({"source": resolver.source_name, "error": str(error)}),
                        file=sys.stderr,
                        flush=True,
                    )
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/search/test_aggregator.py -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Format, lint, commit each file**

```bash
j fmt && j lint

git add iolanta/search/aggregator.py
git commit -m '#412 ➕ `run_search` aggregator with parallel fan-out'

git add tests/search/test_aggregator.py
git commit -m '#412 ➕ test for `run_search` aggregator'
```

---

## Task 10: `search-result` + `jsonl` datatype metadata (YAML-LD)

**Files:**
- Create: `iolanta/facets/search/__init__.py`
- Create: `iolanta/facets/search/data/search_result.yamlld`

This task is purely declarative — no Python tests. A smoke test happens implicitly in Task 12 when the facet is registered.

- [ ] **Step 1: Create the package**

```bash
mkdir -p iolanta/facets/search/data
```

Create `iolanta/facets/search/__init__.py`:
```python
# noqa: D104
```

- [ ] **Step 2: Create the YAML-LD metadata**

Create `iolanta/facets/search/data/search_result.yamlld`:

```yaml
"@context":
  "@import": https://json-ld.org/contexts/dollar-convenience.jsonld
  iolanta: https://iolanta.tech/
  rdfs: "http://www.w3.org/2000/01/rdf-schema#"
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  owl: http://www.w3.org/2002/07/owl#

  $: rdfs:label
  →:
    "@type": "@id"
    "@id": iolanta:outputs
  ⊆:
    "@type": "@id"
    "@id": rdfs:subClassOf
  iolanta:hasDatatypeFacet:
    "@type": "@id"

$included:
  - $id: https://iolanta.tech/datatypes/search-result
    $type: owl:Class
    ⊆: rdfs:Datatype
    $: Search Result
    rdfs:comment: Internal wrapping datatype for an iterable of SearchHit candidates produced by --search.

  - $id: https://iolanta.tech/datatypes/jsonl
    $type: owl:Class
    ⊆: rdfs:Datatype
    $: JSON Lines
    rdfs:comment: Newline-delimited JSON output format. One JSON object per line, terminated by \n.

  - $id: pkg:pypi/iolanta#search-result-jsonl-facet
    $type: iolanta:Facet
    $: Search Result JSONL Facet
    →: https://iolanta.tech/datatypes/jsonl

  - $id: https://iolanta.tech/datatypes/search-result
    iolanta:hasDatatypeFacet:
      - pkg:pypi/iolanta#search-result-jsonl-facet
```

- [ ] **Step 3: Commit each file**

```bash
git add iolanta/facets/search/__init__.py
git commit -m '#412 ➕ `iolanta.facets.search` package'

git add iolanta/facets/search/data/search_result.yamlld
git commit -m '#412 ➕ `search-result` and `jsonl` datatype metadata'
```

---

## Task 11: `SearchResultJsonlFacet`

**Files:**
- Create: `tests/search/test_jsonl_facet.py`
- Create: `iolanta/facets/search/search_result_jsonl.py`

- [ ] **Step 1: Write the failing test**

Create `tests/search/test_jsonl_facet.py`:

```python
"""Test the SearchResultJsonlFacet."""
from unittest.mock import MagicMock

from rdflib import Literal, URIRef

from iolanta.cli.models import JsonLines
from iolanta.facets.errors import FacetNotFound
from iolanta.facets.search.search_result_jsonl import SearchResultJsonlFacet
from iolanta.namespaces import DATATYPES
from iolanta.search.models import SearchHit


def _make_facet(hits, render_returns=None, render_raises_for=None):
    iolanta_mock = MagicMock()

    def fake_render(node, as_datatype):
        uri = str(node)
        if render_raises_for and uri in render_raises_for:
            raise FacetNotFound(node=node)
        return (render_returns or {}).get(uri, "stub-title")

    iolanta_mock.render.side_effect = fake_render

    facet = SearchResultJsonlFacet.__new__(SearchResultJsonlFacet)
    facet.this = Literal(iter(hits), datatype=DATATYPES["search-result"])
    facet.iolanta = iolanta_mock
    return facet, iolanta_mock


def _hit(uri, source="wikidata"):
    return SearchHit(
        uri=uri,
        source=source,
        description=None,
        score=None,
        types=[],
    )


def test_facet_returns_jsonlines_with_one_dict_per_hit():
    hits = [
        _hit("https://example.org/a"),
        _hit("https://example.org/b"),
    ]
    facet, _ = _make_facet(hits)

    result = facet.show()

    assert isinstance(result, JsonLines)
    lines = list(result.lines)
    assert len(lines) == 2
    uris = sorted(line["uri"] for line in lines)
    assert uris == ["https://example.org/a", "https://example.org/b"]
    for line in lines:
        assert set(line.keys()) == {"uri", "source", "title", "description", "score", "types"}
        assert isinstance(line["types"], list)


def test_facet_resolves_titles_via_iolanta_render():
    hits = [_hit("https://example.org/a")]
    facet, iolanta_mock = _make_facet(
        hits,
        render_returns={"https://example.org/a": "Example A"},
    )

    lines = list(facet.show().lines)

    assert lines[0]["title"] == "Example A"
    iolanta_mock.render.assert_called_once_with(
        URIRef("https://example.org/a"),
        as_datatype=DATATYPES.title,
    )


def test_facet_yields_null_title_when_render_raises_facet_not_found():
    hits = [
        _hit("https://example.org/a"),
        _hit("https://example.org/b"),
    ]
    facet, _ = _make_facet(
        hits,
        render_raises_for={"https://example.org/a"},
        render_returns={"https://example.org/b": "B-title"},
    )

    by_uri = {line["uri"]: line for line in facet.show().lines}
    assert by_uri["https://example.org/a"]["title"] is None
    assert by_uri["https://example.org/b"]["title"] == "B-title"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/search/test_jsonl_facet.py -v`

Expected: `ImportError` (no `SearchResultJsonlFacet`).

- [ ] **Step 3: Implement `SearchResultJsonlFacet`**

Create `iolanta/facets/search/search_result_jsonl.py`:

```python
"""JSONL facet for search-result Literals."""
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from documented import DocumentedError
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
                    "uri": hit.uri,
                    "source": hit.source,
                    "title": future.result(),
                    "description": hit.description,
                    "score": hit.score,
                    "types": list(hit.types),
                }

    def _render_title(self, uri: str) -> str | None:
        try:
            return self.iolanta.render(
                URIRef(uri),
                as_datatype=DATATYPES.title,
            )
        except (FacetNotFound, DocumentedError):
            return None
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/search/test_jsonl_facet.py -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Format, lint, commit each file**

```bash
j fmt && j lint

git add iolanta/facets/search/search_result_jsonl.py
git commit -m '#412 ➕ `SearchResultJsonlFacet`'

git add tests/search/test_jsonl_facet.py
git commit -m '#412 ➕ test for `SearchResultJsonlFacet`'
```

---

## Task 12: Register the facet entry-point in `pyproject.toml`

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Locate the existing entry-points block**

Run: `grep -n "select-result-json-facet" pyproject.toml`

Note the line number — the new entry-point goes in the same `[tool.poetry.plugins."iolanta.facets"]` section (or whatever section the existing facet entry-points live in).

- [ ] **Step 2: Add the new entry-point line**

Add this line in the same section as the existing facet entry-points (alphabetical order with the other `*-facet` entries is conventional but not required):

```toml
search-result-jsonl-facet = "iolanta.facets.search.search_result_jsonl:SearchResultJsonlFacet"
```

- [ ] **Step 3: Reinstall the package so the entry-point is registered**

Run: `poetry install`

Expected: clean reinstall (no errors). Iolanta is now aware of the new facet.

- [ ] **Step 4: Smoke-test that the entry-point resolves**

Run:
```bash
python -c "
from importlib.metadata import entry_points
eps = [ep for ep in entry_points(group='iolanta.facets') if ep.name == 'search-result-jsonl-facet']
print(eps[0].load())
"
```

Expected: prints `<class 'iolanta.facets.search.search_result_jsonl.SearchResultJsonlFacet'>`.

(If the group name above doesn't match, replace it with whatever the existing `select-result-json-facet` line is registered under — see the surrounding section header in `pyproject.toml`.)

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml
git commit -m '#412 ➕ `search-result-jsonl-facet` entry-point'
```

---

## Task 13: CLI integration — add `--search` Option to `render_command`

**Files:**
- Modify: `iolanta/cli/main.py`
- Create: `tests/search/test_cli_search.py`

- [ ] **Step 1: Write the failing end-to-end test**

Create `tests/search/test_cli_search.py`:

```python
"""End-to-end test for `iolanta --search ... --as jsonl`."""
import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from iolanta.cli.main import app
from iolanta.search.models import SearchHit


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


def _hit(source: str, uri: str) -> SearchHit:
    return SearchHit(
        uri=uri,
        source=source,
        description=None,
        score=None,
        types=[],
    )


@patch("iolanta.cli.main.run_search")
def test_search_jsonl_emits_one_line_per_hit(mock_run_search, runner):
    mock_run_search.return_value = iter([
        _hit("wikidata", "https://www.wikidata.org/entity/Q34981"),
        _hit("dbpedia", "http://dbpedia.org/resource/Isaac_Asimov"),
    ])
    with patch(
        "iolanta.facets.search.search_result_jsonl."
        "SearchResultJsonlFacet._render_title",
        return_value="stub-title",
    ):
        result = runner.invoke(app, ["--search", "Isaac Asimov", "--as", "jsonl"])

    assert result.exit_code == 0
    lines = [
        json.loads(line) for line in result.stdout.splitlines() if line.strip()
    ]
    assert len(lines) == 2
    uris = sorted(line["uri"] for line in lines)
    assert uris == [
        "http://dbpedia.org/resource/Isaac_Asimov",
        "https://www.wikidata.org/entity/Q34981",
    ]


@patch("iolanta.cli.main.run_search")
def test_search_default_as_raises_facet_not_found(mock_run_search, runner):
    """Bare `iolanta --search Asimov` (no --as) is the deliberate v0 crash."""
    mock_run_search.return_value = iter([
        _hit("wikidata", "https://www.wikidata.org/entity/Q34981"),
    ])
    result = runner.invoke(app, ["--search", "Isaac Asimov"])

    assert result.exit_code == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/search/test_cli_search.py -v`

Expected: failure — `--search` is not a recognized option (Typer error) or the option exists but does nothing.

- [ ] **Step 3: Add `--search` to `render_command` in `iolanta/cli/main.py`**

Three edits to `iolanta/cli/main.py`:

a) Add the import near the top, alongside the existing `from iolanta.cli.models import JsonLines, LogLevel`:

```python
from iolanta.search.aggregator import run_search
```

b) Modify the `render_command` signature in `iolanta/cli/main.py:233-256` to add a new `search` parameter between `query` and `as_datatype`. The exact insertion (preserve existing surrounding parameters):

```python
@app.command(name="render")
def render_command(  # noqa: WPS231, WPS238, WPS210, C901
    url: Annotated[str | None, Argument()] = None,
    query: Annotated[
        str | None,
        Option(
            "--query",
            help="SPARQL query to execute.",
        ),
    ] = None,
    search: Annotated[
        str | None,
        Option(
            "--search",
            help="Notion to look up across linked-data search APIs.",
        ),
    ] = None,
    as_datatype: Annotated[
        str | None,
        Option(
            "--as",
        ),
    ] = None,
    language: Annotated[
        str,
        Option(
            help="Data language to prefer.",
        ),
    ] = DEFAULT_LANGUAGE,
    log_level: LogLevel = LogLevel.ERROR,
):
```

c) Add a new `--search` handling block inside `render_command`, immediately after the existing `--query` block (which is at `iolanta/cli/main.py:258-284`) and before the `if url is None:` guard. Insert this block:

```python
    if search is not None:
        # Default to interactive (matches `iolanta <url>`); v0 has no interactive
        # facet for search-result, so a bare `--search` will FacetNotFound — by design.
        if as_datatype is None:
            as_datatype = "https://iolanta.tech/cli/interactive"

        search_node = Literal(
            run_search(search),
            datatype=DATATYPES["search-result"],
        )

        try:
            renderable = render_and_return(
                node=search_node,
                as_datatype=as_datatype,
                language=language,
                log_level=log_level,
            )
        except (DocumentedError, FacetNotFound) as error:
            handle_error(error, log_level, use_markdown=True)
        except Exception as error:  # noqa: BLE001  intentional last-resort path mirrors --query
            handle_error(error, log_level, use_markdown=False)
        else:
            print_renderable(renderable)
        return
```

d) Update the `if url is None:` guard at `iolanta/cli/main.py:286-288` to mention `--search`:

```python
    if url is None:
        console.print("Error: URL, --query, or --search must be provided")
        raise Exit(1)
```

(The `noqa: BLE001` comment for the broad-Exception path matches what the existing `--query` branch already does at line 280–281; do not introduce a new lint suppression where the existing one isn't already in use. If your local lint complains about this catch and the `--query` branch above passes lint without suppression, drop the `# noqa` and keep the catch — match whatever the immediately-prior `--query` branch does.)

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/search/test_cli_search.py -v`

Expected: 2 tests PASS.

- [ ] **Step 5: Manual smoke test**

In a new terminal (so the entry-points reload):

```bash
# Should print parseable JSONL on stdout (real network calls — needs internet)
iolanta --search "Isaac Asimov" --as jsonl | jq -c .

# Should exit 1 with FacetNotFound (no interactive facet for search-result in v0)
iolanta --search "Isaac Asimov"
echo "exit code: $?"
```

Expected: first command emits valid JSONL (lines with `uri`, `source`, `title`, etc.); second command exits 1.

- [ ] **Step 6: Format, lint, commit**

```bash
j fmt && j lint   # fix touched-file findings

git add iolanta/cli/main.py
git commit -m '#412 ➕ `--search` option to `render_command`'

git add tests/search/test_cli_search.py
git commit -m '#412 ➕ end-to-end test for `iolanta --search`'
```

---

## Task 14: `docs/datatypes/jsonl.md` documentation page

**Files:**
- Create: `docs/datatypes/jsonl.md`

- [ ] **Step 1: Create the page**

Create `docs/datatypes/jsonl.md` (mirrors `docs/datatypes/mermaid.md`):

```markdown
---
"@context": ../context.yamlld

$id: https://iolanta.tech/datatypes/jsonl
$type: iolanta:OutputDatatype
$: JSON Lines
hide: toc

⊆: xsd:string

rdfs:comment: >
  [JSON Lines](https://jsonlines.org/) (newline-delimited JSON) output format.
  One JSON object per line, terminated by `\n`. Suitable for streaming
  pipelines: each line is independently parseable, and consumers can process
  output incrementally (e.g. piping through `jq -c .`).

  Used by `iolanta --search "<notion>" --as jsonl`, which fans out to four
  linked-data search APIs (Wikidata Reconciliation, DBpedia Lookup,
  Nanopublications Lucene SAIL, and LOV term search) and emits one candidate
  URI per line.

  Each line carries the fields `uri`, `source`, `title`, `description`,
  `score`, and `types`. The `score` field is **per-source**, not
  cross-source: Wikidata reconciliation returns floats in [0, 1], the
  Nanopublications Lucene endpoint returns arbitrary positive floats, LOV
  uses its own scale, and DBpedia returns `null`. Compare scores within a
  single `source` value, never across.
---

{{ URIRef("https://iolanta.tech/datatypes/jsonl") | as('mkdocs-material-insiders-markdown') }}
```

- [ ] **Step 2: Verify the page renders through Iolanta itself**

Run: `iolanta docs/datatypes/jsonl.md`

Expected: renders without errors (per AGENTS.md D02-style verification of YAML-LD pages).

- [ ] **Step 3: Verify the page is reachable in the local MkDocs server**

If `j serve` is already running on `localhost:6451`, browse to `http://localhost:6451/datatypes/jsonl/`. Otherwise: `mkdocs build` and grep the built site:

```bash
mkdocs build
find site/datatypes -name 'jsonl*'
```

Expected: the page appears under `site/datatypes/jsonl/`.

- [ ] **Step 4: Commit**

```bash
git add docs/datatypes/jsonl.md
git commit -m '#412 ➕ `jsonl` output-datatype docs page'
```

---

## Task 15: Jeeves task `j refresh-search-fixtures`

**Files:**
- Modify: `jeeves/__init__.py`

- [ ] **Step 1: Append the new task at the end of `jeeves/__init__.py`**

Add this code at the end of `jeeves/__init__.py`:

```python
def refresh_search_fixtures(notion: str = "Isaac Asimov"):
    """Recapture the four search-resolver fixtures from live APIs.

    Manual command. Not run in CI. Use this when an upstream API contract drift
    is suspected and the captured fixtures need refreshing.
    """
    fixtures_dir = project_directory.parent / "tests/search/fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers["User-Agent"] = "iolanta-fixture-refresh"

        # Wikidata Reconciliation
        wikidata_response = session.get(
            "https://wikidata-reconciliation.wmcloud.org/en/api",
            params={
                "queries": json.dumps({"q0": {"query": notion, "limit": 10}}),
            },
            timeout=30,
        )
        wikidata_response.raise_for_status()
        (fixtures_dir / "wikidata_asimov.json").write_text(
            json.dumps(wikidata_response.json(), indent=2, ensure_ascii=False),
        )
        console.print("[green]Refreshed[/green] wikidata_asimov.json")

        # DBpedia Lookup
        dbpedia_response = session.get(
            "https://lookup.dbpedia.org/api/search",
            params={"query": notion, "maxResults": 10, "format": "JSON"},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        dbpedia_response.raise_for_status()
        (fixtures_dir / "dbpedia_asimov.json").write_text(
            json.dumps(dbpedia_response.json(), indent=2, ensure_ascii=False),
        )
        console.print("[green]Refreshed[/green] dbpedia_asimov.json")

        # Nanopublications Lucene SAIL
        sparql_query = (
            'PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>\n'
            'SELECT DISTINCT ?subj ?score WHERE {\n'
            '  ?subj search:matches [\n'
            f'    search:query "{notion}" ;\n'
            '    search:score ?score\n'
            '  ] .\n'
            '} ORDER BY DESC(?score) LIMIT 10'
        )
        nanopub_response = session.get(
            "https://query.knowledgepixels.com/repo/text",
            params={"query": sparql_query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=30,
        )
        nanopub_response.raise_for_status()
        (fixtures_dir / "nanopub_asimov.sparql-json").write_text(
            json.dumps(nanopub_response.json(), indent=2, ensure_ascii=False),
        )
        console.print("[green]Refreshed[/green] nanopub_asimov.sparql-json")

        # LOV — class/property query (e.g. "author of") and zero-hits entity case
        lov_author_response = session.get(
            "https://lov.linkeddata.es/dataset/lov/api/v2/term/search",
            params={"q": "author of"},
            timeout=30,
        )
        lov_author_response.raise_for_status()
        (fixtures_dir / "lov_author.json").write_text(
            json.dumps(lov_author_response.json(), indent=2, ensure_ascii=False),
        )
        console.print("[green]Refreshed[/green] lov_author.json")

        lov_asimov_response = session.get(
            "https://lov.linkeddata.es/dataset/lov/api/v2/term/search",
            params={"q": notion},
            timeout=30,
        )
        lov_asimov_response.raise_for_status()
        (fixtures_dir / "lov_asimov.json").write_text(
            json.dumps(lov_asimov_response.json(), indent=2, ensure_ascii=False),
        )
        console.print("[green]Refreshed[/green] lov_asimov.json")
```

- [ ] **Step 2: Verify the command is registered**

Run: `j --help | grep refresh-search-fixtures`

Expected: the command appears in the help listing.

- [ ] **Step 3: Run the command end-to-end (real network)**

Run: `j refresh-search-fixtures`

Expected: prints five "Refreshed ..." lines. Each fixture file now contains real upstream data.

- [ ] **Step 4: Re-run the test suite to confirm tests still pass against refreshed fixtures**

Run: `pytest tests/search/`

Expected: all tests still pass. If any test breaks because the real upstream response shape differs from the handcrafted fixture (e.g. missing `description` on a hit the test asserted on), update the test to be more flexible (assert on shape, not exact values where the upstream is variable). Re-run.

- [ ] **Step 5: Decide whether to keep the refreshed fixtures**

If the refreshed fixtures look reasonable (richer than the handcrafted ones, no test breakage requiring assertion changes), commit them. Otherwise: `git checkout tests/search/fixtures/` to revert. Either way, the `j` command itself is the deliverable from this task.

- [ ] **Step 6: Format, lint, commit**

```bash
j fmt && j lint

git add jeeves/__init__.py
git commit -m '#412 ➕ `j refresh-search-fixtures` task'

# If you decided to keep refreshed fixtures (and only those that meaningfully changed):
# Commit each fixture file separately per AGENTS.md C10, e.g.:
# git add tests/search/fixtures/wikidata_asimov.json
# git commit -m '#412 Refresh `wikidata_asimov.json` from live API'
# (...repeat for each)
```

---

## Task 16: Validation runbook (full)

This is the spec's Validation section, executed end-to-end. No code changes — this is the gating sequence before declaring the issue done.

- [ ] **Step 1: Format and lint the whole project**

Run: `j fmt && j lint`

Fix all WPS findings in files touched by this issue. Per AGENTS.md F02: never dismiss WPS errors as "expected" or "normal." Per F03: if `j lint` reports unrelated project-wide errors, report them in the PR description rather than fixing silently.

- [ ] **Step 2: Run the full search test suite**

Run: `pytest tests/search/ -v`

Expected: every test passes (resolvers × 4, aggregator, JSONL facet, end-to-end CLI, JsonLines + print_renderable, SearchHit).

- [ ] **Step 3: Run the entire project test suite to catch regressions**

Run: `pytest tests/ -v`

Expected: no new failures introduced. (Pre-existing failures, if any, should be flagged in the PR description but not "fixed" silently.)

- [ ] **Step 4: Manual end-to-end smoke (real network)**

Run:
```bash
iolanta --search "Isaac Asimov" --as jsonl | jq -c .
```

Expected: streaming JSONL on stdout, each line a complete JSON object with `uri`, `source`, `title`, `description`, `score`, `types`. Some titles may be `null` if the URI dereferencing fails — that's allowed.

Run:
```bash
iolanta --search "Isaac Asimov"
echo "exit code: $?"
```

Expected: exits 1 with `FacetNotFound` for `https://iolanta.tech/cli/interactive` (the v0 crash, by design).

- [ ] **Step 5: Verify the new docs page renders**

Run: `iolanta docs/datatypes/jsonl.md`

Expected: renders the YAML-LD page without error.

- [ ] **Step 6: Verify MkDocs exclusion still works after all the spec/plan files were committed**

Run: `mkdocs build && find site/ -path '*superpowers*'`

Expected: `mkdocs build` succeeds; the `find` returns zero results (the `exclude_docs: superpowers/` from the spec commit keeps `docs/superpowers/` out of the build).

- [ ] **Step 7: Verify `iolanta --help` advertises `--search`**

Run: `iolanta --help`

Expected: the help text lists `--search` alongside `--query` and `--as`.

- [ ] **Step 8: Push the branch and open the PR**

```bash
git push -u origin 412-implement-iolanta-search-as-jsonl

gh pr create --title 'Implement `iolanta --search ... --as jsonl` (#412)' --body "$(cat <<'EOF'
## Summary
- Adds `iolanta --search "<notion>" --as jsonl` that fans out to four linked-data search APIs in parallel (Wikidata Reconciliation, DBpedia Lookup, Nanopublications Lucene SAIL, LOV) and emits one JSON object per candidate on stdout.
- Per-source failures go to stderr as one-line JSON; successful sources still yield. Exit 1 only when every source fails or when the chosen `--as` facet does not exist.
- v0 ships only the JSONL facet — bare `iolanta --search Asimov` raises `FacetNotFound` by design.
- Zero new dependencies; reuses `requests` and `concurrent.futures.ThreadPoolExecutor`.

Closes #412

Spec: `docs/superpowers/specs/2026-05-03-iolanta-search-design.md` (in the GitHub source — excluded from the public docs site via `exclude_docs:`).

## Test plan
- [x] `pytest tests/search/` — all layers pass (resolvers × 4, aggregator, JSONL facet, end-to-end CLI).
- [x] `pytest tests/` — no regressions in the full suite.
- [x] `iolanta --search "Isaac Asimov" --as jsonl | jq -c .` — emits valid streaming JSONL.
- [x] `iolanta --search "Isaac Asimov"` — exits 1 with `FacetNotFound` (deliberate v0 crash).
- [x] `iolanta docs/datatypes/jsonl.md` — new docs page renders cleanly.
- [x] `mkdocs build && find site/ -path '*superpowers*'` — `docs/superpowers/` excluded from public site.
- [x] `iolanta --help` — advertises `--search`.
EOF
)"
```

---

## Self-review summary (run before declaring this plan complete)

The plan author should mentally tick each of these against the spec sections before handing off:

- [x] **CLI surface** (spec §CLI surface) — Task 13 adds `--search` Option to `render_command`, with the deliberate `FacetNotFound` for bare `--search`.
- [x] **Module layout** (spec §Architecture) — Tasks 2, 3, 4–7, 9 build `iolanta/search/`; Tasks 10, 11 build `iolanta/facets/search/`; Task 1 modifies `iolanta/cli/`.
- [x] **Four resolvers + contracts** (spec §The four resolvers) — Tasks 4–7, one per resolver, each with fixture + TDD + commit.
- [x] **Aggregator with `Iterable[SearchHit]`** (spec §Data flow §2) — Task 9, with parallelism + per-source-error stderr lines verified.
- [x] **`search-result` + `jsonl` datatypes** (spec §The search-result datatype and JSONL facet) — Task 10 adds the YAML-LD; Task 12 wires the entry-point.
- [x] **`SearchResultJsonlFacet`** (spec §JsonLines helper and print_renderable extension) — Task 11.
- [x] **`JsonLines` + `print_renderable` extension** (spec §JsonLines helper) — Task 1.
- [x] **`docs/datatypes/jsonl.md`** (spec §Documentation deliverables) — Task 14, with the per-source `score` caveat included.
- [x] **`j refresh-search-fixtures`** (spec §Testing) — Task 15.
- [x] **Validation runbook** (spec §Validation) — Task 16, all seven steps from the spec.
- [x] **MkDocs exclusion** (spec §MkDocs exclusion) — already landed in commit `accca1c` on this branch; Task 16 step 6 re-verifies.
- [x] **No `--limit` flag, no interactive facet, no `--as table`, no nanopub `npx:introduces` dereference, no enrichment** (spec §Non-goals) — explicitly out of scope; the plan does not introduce them.
