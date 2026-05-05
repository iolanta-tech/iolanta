# `iolanta --search` design

**Date:** 2026-05-03
**Status:** Draft (awaiting user review)
**Primary consumer:** the next edition of the `/find-url-for` skill (in `~/projects/nanopublishing/skills/find-url-for/SKILL.md`), which today fans out to four linked-data search APIs from a Claude skill and will instead invoke `iolanta --search "<notion>" --as jsonl` once this lands.

## Goal

Add a `--search` option to the `iolanta` CLI that takes a notion (a person, place, work, organization, concept, class, or property), fans out to four linked-data search sources in parallel, and emits a stream of candidate URIs in JSON Lines for downstream consumption. The command consolidates a workflow that today lives entirely inside the `/find-url-for` skill, so the skill can shrink to a thin wrapper.

## Non-goals (v0)

- No interactive TUI picker. `iolanta --search "Asimov"` with no `--as` raises `FacetNotFound`. By design.
- No `--as table` facet. Same crash mode as above.
- No `--limit` flag. Hardcoded internal cap of 10 hits per source.
- No nanopublication `npx:introduces` dereference. Nanopub URIs are emitted raw; the consumer dereferences if it wants the term URI rather than the nanopub URI.
- No enrichment (`wbgetentities`, LODsyndesis, Falcon 2.0). The skill consumer can call those separately. Iolanta's only "enrichment" is calling `render(uri, as=DATATYPES.title)` to fill in the `title` field.
- No upstream-response caching. Each invocation is a fresh fan-out.
- No true end-to-end interleaved streaming pipeline. The JSONL facet collects all search hits before submitting title renders. Wall-clock latency is `max(source_call) + max(title_render)`, not the fully-interleaved minimum. Revisit if latency complaints surface.

## CLI surface

`--search "<notion>"` is a new `Option` on the existing `render_command` in `iolanta/cli/main.py`, alongside `--query`. Mutually exclusive with the positional `url` argument and with `--query`, validated by an explicit check in the same style as the existing `url` vs `--query` guard.

`--as` defaults to `https://iolanta.tech/cli/interactive` (matching `iolanta <url>`), so a bare `iolanta --search Asimov` raises `FacetNotFound` in v0.

```console
$ iolanta --search "Isaac Asimov" --as jsonl    # primary v0 use
$ iolanta --search "Isaac Asimov"               # raises FacetNotFound (no interactive facet)
```

## Architecture

```
iolanta/search/
  __init__.py
  models.py                      # SearchHit dataclass
  aggregator.py                  # run_search(notion) -> Iterable[SearchHit]
  resolvers/
    __init__.py
    base.py                      # SearchResolver protocol
    nanopublications.py
    wikidata.py
    dbpedia.py
    lov.py

iolanta/facets/search/
  __init__.py
  data/
    search_result.yamlld         # datatype + facet metadata
  search_result_jsonl.py         # SearchResultJsonlFacet

iolanta/cli/
  main.py                        # add --search Option to render_command, add JsonLines case to print_renderable
  models.py                      # add JsonLines dataclass

docs/datatypes/jsonl.md          # new output-datatype docs page (mirrors mermaid.md)
pyproject.toml                   # add `search-result-jsonl-facet` entry-point
mkdocs.yml                       # add `exclude_docs: superpowers/` so this spec doesn't ship on the site
```

### Data flow

1. CLI parses `--search` → calls `run_search(notion)`.
2. `run_search` opens a `requests.Session`, fans out four resolvers in a `ThreadPoolExecutor(max_workers=4)`, and `yield from` each future's result as `as_completed` reports them. Per-resolver exceptions become single-line JSON on stderr; successful sources still yield. Per-call `result(timeout=10)` enforces a 10s ceiling per source.
3. CLI wraps the iterable: `Literal(run_search(notion), datatype=DATATYPES["search-result"])`.
4. CLI hands off to the existing `render_and_return` path with the user-chosen `as_datatype` (default → `https://iolanta.tech/cli/interactive` → `FacetNotFound` in v0; `--as jsonl` → `SearchResultJsonlFacet`).
5. `SearchResultJsonlFacet.show()` returns `JsonLines(lines=generator)` where the generator drains the wrapped iterable through a second `ThreadPoolExecutor(max_workers=8)` that calls `iolanta.render(URIRef(hit.uri), as_datatype=DATATYPES.title)` for each hit, yielding a dict per hit in title-completion order.
6. `print_renderable` matches the `JsonLines` case and writes one `json.dumps(line, ensure_ascii=False) + "\n"` per dict, flushing after each.

### Concurrency model

- One `requests.Session` per CLI invocation (created in `run_search`, closed via `with`).
- Two `ThreadPoolExecutor`s — the aggregator's (4 workers, one per source) and the JSONL facet's (8 workers, for title rendering, which itself may dereference unfamiliar URIs). They *overlap in time*: the facet's pool opens and starts submitting title renders as soon as the aggregator's first hits arrive (the dict-comprehension that submits title work drains the aggregator's generator, which keeps the aggregator's pool alive). The aggregator's pool shuts down once its generator is exhausted; the title pool then drains via `as_completed`.
- `as_completed` is the only sync primitive. No `asyncio`.
- `requests` reused as the HTTP library to match the existing `iolanta/sparqlspace/processor.py:11` import. Zero new dependencies.

## The four resolvers

Common protocol (`iolanta/search/resolvers/base.py`):

```python
class SearchResolver(Protocol):
    source_name: str   # "wikidata" | "dbpedia" | "nanopublication" | "lov"
    def search(self, notion: str, session: requests.Session) -> list[SearchHit]: ...
```

`SearchHit` (`iolanta/search/models.py`):

```python
@dataclass(frozen=True)
class SearchHit:
    uri: str
    source: str
    description: str | None
    score: float | None
    types: list[str]
    # NOTE: no `title` field — title is resolved by the JSONL facet via render(uri, as_datatype=DATATYPES.title)
```

| Source | Endpoint | Response → `SearchHit` |
|---|---|---|
| **Wikidata Reconciliation** | `GET https://wikidata-reconciliation.wmcloud.org/en/api?queries={"q0":{"query":"<notion>","limit":10}}` | `uri = "https://www.wikidata.org/entity/" + result.id`; `description = result.description`; `score = result.score`; `types = ["https://www.wikidata.org/entity/" + t.id for t in result.type]` |
| **DBpedia Lookup** | `GET https://lookup.dbpedia.org/api/search?query=<notion>&maxResults=10&format=JSON`, header `Accept: application/json` | `uri = doc.resource[0]`; `description = doc.comment[0] if doc.comment else None`; `score = None`; `types = doc.type or []` |
| **Nanopublications (Lucene SAIL)** | `GET https://query.knowledgepixels.com/repo/text?query=<SPARQL>`, header `Accept: application/sparql-results+json` (template below) | `uri = binding["subj"]["value"]` (raw nanopub URI; see caveat); `description = None`; `score = float(binding["score"]["value"])`; `types = []` |
| **LOV term search** | `GET https://lov.linkeddata.es/dataset/lov/api/v2/term/search?q=<notion>` | `uri = result.uri[0]`; `description = result.comment[0] if result.comment else None`; `score = result.score`; `types = result.type` |

LOV is always called, even for entity searches (it returns 0 hits for entities — that's the right scope, not a failure). No heuristic source-skipping: the JSONL output is *complete* by definition, and consumers don't have to wonder whether Iolanta skipped a source for them.

Nanopublications SPARQL template (hardcoded in `nanopublications.py`):

```sparql
PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>
SELECT DISTINCT ?subj ?score WHERE {
  ?subj search:matches [
    search:query "<notion-escaped>" ;
    search:score ?score
  ] .
} ORDER BY DESC(?score) LIMIT 10
```

### Documented caveats

1. **Nanopub URIs are nanopub URIs, not term URIs.** The skill notes: "the term URI lives in the nanopub's `pubinfo` graph as `npx:introduces <term-uri>`." v0 does not dereference. Consumers (`/find-url-for`) do this on their own if they want the term URI rather than the nanopub URI.
2. **`score` is per-source, not cross-source.** Wikidata reconciliation: 0–1 float. Nanopubs Lucene: arbitrary positive. LOV: own scale. DBpedia: `null`. Compare scores within a `source` value, not across. This is documented on `docs/datatypes/jsonl.md`.

## The `search-result` datatype and JSONL facet

Two new datatypes registered in `iolanta/facets/search/data/search_result.yamlld` (mirrors `iolanta/facets/query/data/query_result.yamlld:20-58`):

- `https://iolanta.tech/datatypes/search-result` — internal wrapping datatype (no docs page; like `sparql-select-result`, the user never types `--as search-result`).
- `https://iolanta.tech/datatypes/jsonl` — output datatype (gets a docs page at `docs/datatypes/jsonl.md`; the user types `--as jsonl`).

Convention pinned: **output datatypes get docs pages; internal wrapping datatypes don't.** This rule lives in this spec; it is not promoted to AGENTS.md unless a second instance arises.

One facet registered for v0:

```yaml
- $id: pkg:pypi/iolanta#search-result-jsonl-facet
  $type: iolanta:Facet
  $: Search Result JSONL Facet
  →: https://iolanta.tech/datatypes/jsonl

- $id: https://iolanta.tech/datatypes/search-result
  iolanta:hasDatatypeFacet:
    - pkg:pypi/iolanta#search-result-jsonl-facet
```

Entry-point in `pyproject.toml` (matching the `select-result-json-facet` line):
```toml
search-result-jsonl-facet = "iolanta.facets.search.search_result_jsonl:SearchResultJsonlFacet"
```

### `JsonLines` helper and `print_renderable` extension

The facet does not perform I/O. It returns a `JsonLines` wrapper holding a lazy iterable of dicts; the CLI's `print_renderable` streams them.

```python
# iolanta/cli/models.py — alongside LogLevel
@dataclass(frozen=True)
class JsonLines:
    """Streamable JSONL output. Each item becomes one line in the rendered output."""
    lines: Iterable[dict]
```

```python
# iolanta/facets/search/search_result_jsonl.py
class SearchResultJsonlFacet(RichFacet):
    META = META

    def show(self) -> Renderable:
        if not isinstance(self.this, Literal):
            raise NotALiteral(node=self.this)
        return JsonLines(lines=self._stream_lines(self.this.value))

    def _stream_lines(self, hits: Iterable[SearchHit]) -> Iterable[dict]:
        with ThreadPoolExecutor(max_workers=8) as pool:
            in_flight = {pool.submit(self._render_title, hit.uri): hit for hit in hits}
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
            return self.iolanta.render(URIRef(uri), as_datatype=DATATYPES.title)
        except (FacetNotFound, DocumentedError):
            return None
```

```python
# iolanta/cli/main.py — extend the existing print_renderable
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

The `Literal` wraps a single-use generator. The facet must iterate the underlying iterable exactly once. Documented in the facet docstring; not enforced at runtime (per AGENTS.md F07, no defensive code for invariants the type system protects).

### Constraint: `Literal.value` round-trip

The CLI wraps the iterable in `Literal(run_search(notion), datatype=DATATYPES["search-result"])` and the facet reads it back with `self.this.value`. This relies on the same rdflib behavior the existing `--query` path depends on (`iolanta/cli/main.py:152-165`): for unrecognized datatypes, rdflib stores the original Python object accessible via `.value`. If this assumption breaks, both `--search` and `--query` break — and we mirror exactly the established pattern, so the risk is bounded to "if `--query` works, `--search` works."

## Errors and exit codes

- A resolver raising `requests.RequestException`, `TimeoutError`, or `ValueError` is caught in the aggregator and emits one stderr line of shape `{"source": "<name>", "error": "<message>"}`. Other sources still yield. The exception list is explicit per AGENTS.md F04.
- A title `render()` raising `FacetNotFound` or `DocumentedError` becomes `title: null` for that line. URI is the load-bearing field; missing title is recoverable.
- **Exit codes:** exit 1 if (a) every source errored, or (b) the chosen `--as` facet does not exist (the v0 default-`--as` crash). Otherwise exit 0 — including the case where all sources succeed but return zero hits (empty stdout, exit 0, no error lines on stderr).

## Testing

Test layout:

```
tests/search/
  __init__.py
  conftest.py                       # shared fixtures: mocked Session, sample API responses
  fixtures/
    wikidata_asimov.json
    dbpedia_asimov.json
    nanopub_asimov.sparql-json
    lov_author.json
    lov_asimov.json                 # zero-hit case for entity-search vs. LOV
  test_resolvers/
    test_wikidata.py
    test_dbpedia.py
    test_nanopublications.py
    test_lov.py
  test_aggregator.py
  test_jsonl_facet.py
  test_cli_search.py
```

Four layers, each with one job:

1. **Resolver unit tests** — happy path + zero hits + malformed response per resolver. Captured fixture JSON files double as upstream-shape documentation. No network in CI.
2. **Aggregator test** — patch `RESOLVERS` with sleeping/canned/raising stubs. Assert: parallel fan-out (wall time ≈ slowest stub), stderr error-line shape on raise, successful sources yield even when one fails, per-call timeout enforced.
3. **JSONL facet test** — instantiate the facet with a `Literal` wrapping a known list of `SearchHit`. Patch `iolanta.render(..., as_datatype=DATATYPES.title)` to return canned titles. Assert: one dict per hit in agreed schema, `types` always a list, `FacetNotFound` for one URI yields `title: None` for only that line, parallel title resolution observable.
4. **End-to-end CLI test** — Typer's `CliRunner` runs `iolanta --search "Asimov" --as jsonl` against a fully-mocked `requests.Session`. Assert: stdout is parseable JSONL with expected URIs; stderr is clean for all-success; stderr contains source-error JSON for failure scenarios; bare `iolanta --search Asimov` raises `FacetNotFound` (the deliberate v0 crash).

Explicit non-tests for v0:
- No live API hits in CI.
- No real-graph title rendering.
- No wall-clock performance thresholds (parallelism is verified structurally, not timed).

New jeeves task: `j refresh-search-fixtures` recaptures the four upstream JSON fixtures by hitting live APIs with a known notion (e.g. "Isaac Asimov") and writing the responses into `tests/search/fixtures/`. Manual, not run in CI.

Code-style conformance per AGENTS.md F04 / F08 / F09: every `try/except` lists specific exceptions (no bare `Exception`), type-dispatch uses `match/case` (not `isinstance` chains), tests prefer repeated string literals over helper constants. The actual lint/format invocation lives in the Validation section below.

## Validation

Run these in order during implementation. Fix issues before reporting any task complete (per AGENTS.md F12).

1. **Format Python sources:** `j fmt`. Run after every batch of Python edits.
2. **Lint Python sources:** `j lint`. Fix all WPS findings in touched files (per AGENTS.md F02 — never dismiss WPS errors as "expected"). If `j lint` reports unrelated project-wide errors not introduced by this work, report that explicitly rather than silently fixing them (per F03).
3. **Run the new test layers:**
   - `pytest tests/search/test_resolvers/` — per-resolver unit tests against captured fixtures.
   - `pytest tests/search/test_aggregator.py` — parallel fan-out, partial-failure stderr lines, per-source timeout.
   - `pytest tests/search/test_jsonl_facet.py` — facet contract, `JsonLines` shape, parallel title resolution, `title: null` on `FacetNotFound`.
   - `pytest tests/search/test_cli_search.py` — Typer `CliRunner` end-to-end, default-`--as` `FacetNotFound` crash.
   - Or in one shot: `pytest tests/search/`.
4. **Manual end-to-end smoke** (not in CI):
   - `iolanta --search "Isaac Asimov" --as jsonl` — confirm parseable JSONL on stdout, clean stderr, exit 0. Pipe through `jq -c .` to verify each line is valid JSON.
   - `iolanta --search "Isaac Asimov"` — confirm `FacetNotFound` and exit 1 (the deliberate v0 crash).
5. **Verify the new `docs/datatypes/jsonl.md` page is well-formed YAML-LD** by rendering it through Iolanta itself (per AGENTS.md D02 idiom): `iolanta docs/datatypes/jsonl.md`. The page should render without errors.
6. **Verify the MkDocs exclusion works:**
   - `mkdocs build` — should succeed without warnings about `docs/superpowers/`.
   - `find site/ -path '*superpowers*'` — should return zero results.
7. **Verify `j refresh-search-fixtures` works end-to-end** (one-shot manual run): `j refresh-search-fixtures` against live APIs. Confirm fixtures regenerate. If unintended diffs appear, revert them (per the principle of treating fixture changes as deliberate).

## Documentation deliverables

- `docs/datatypes/jsonl.md` — new YAML-LD page mirroring `docs/datatypes/mermaid.md`. Declares `https://iolanta.tech/datatypes/jsonl` as `iolanta:OutputDatatype` ⊆ `xsd:string`, with `rdfs:comment` describing JSON Lines and a usage note about per-source `score` semantics and the four current sources.
- No README changes (the README stays minimal; `--search` is discoverable via `iolanta --help`).
- No AGENTS.md changes (the existing **J00–J05** rules cover the new jeeves task; **F04–F12** cover the linting conventions).

## MkDocs exclusion

`mkdocs.yml` gains a top-level `exclude_docs:` block to keep `docs/superpowers/` (this spec and any future ones) out of the public site:

```yaml
exclude_docs: |
  superpowers/
```

Native to MkDocs ≥ 1.5; the project uses 1.6.1 (per `poetry.lock`). No new plugin needed.

## Sample sessions

Happy path:

```console
$ iolanta --search "Isaac Asimov" --as jsonl
{"uri":"https://www.wikidata.org/entity/Q34981","source":"wikidata","title":"Isaac Asimov","description":"American writer and biochemist (1920–1992)","score":0.94,"types":["https://www.wikidata.org/entity/Q5"]}
{"uri":"http://dbpedia.org/resource/Isaac_Asimov","source":"dbpedia","title":"Isaac Asimov","description":"Russian-born American author...","score":null,"types":["http://dbpedia.org/ontology/Person","http://dbpedia.org/ontology/Writer"]}
{"uri":"http://purl.org/np/RA7Y...","source":"nanopublication","title":"Isaac Asimov (term)","description":null,"score":12.4,"types":[]}

$ iolanta --search "Isaac Asimov"
Error: No facet found for datatype https://iolanta.tech/cli/interactive on a search-result Literal.
$ echo $?
1
```

Partial failure (LOV times out):

```console
$ iolanta --search "Isaac Asimov" --as jsonl 2>errs.log
{"uri":"https://www.wikidata.org/entity/Q34981","source":"wikidata", ...}
{"uri":"http://dbpedia.org/resource/Isaac_Asimov","source":"dbpedia", ...}
{"uri":"http://purl.org/np/RA7Y...","source":"nanopublication", ...}

$ cat errs.log
{"source":"lov","error":"HTTPSConnectionPool(host='lov.linkeddata.es'): Read timed out."}
```

Primary v0 consumer (`/find-url-for`):

```python
import json, subprocess
result = subprocess.run(
    ["iolanta", "--search", notion, "--as", "jsonl"],
    capture_output=True, text=True, check=True,
)
candidates = [json.loads(line) for line in result.stdout.splitlines() if line]
# rank, dedupe, prefer nanopub > wikidata > dbpedia, return top
```
