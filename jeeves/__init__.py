# noqa: WPS412, WPS400
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re

import funcy
import rdflib
import requests
import sh
import yaml
import yaml_ld

# from jeeves_yeti_pyproject import flakeheaven  # Skipped due to compatibility issues with Python 3.12+
from jeeves_yeti_pyproject.mypy import construct_mypy_flags
from rich.console import Console

from jeeves.functionality_score import (  # noqa
    calculate_functionality_score_for_rare_predicates,
)

gh = sh.gh.bake(_env={**os.environ, "NO_COLOR": "1"})

project_directory = Path(__file__).parent
artifacts = project_directory / "tests/artifacts"
pytest_xml = artifacts / "pytest.xml"

console = Console()

_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def deploy_to_github_pages():
    """Build the docs & deploy → gh-pages branch."""
    try:
        sh.mkdocs("gh-deploy", "--force", "--clean", "--verbose")
    except sh.ErrorReturnCode as error:
        raise ValueError(error.stderr.decode("utf-8"))


def serve():
    """
    Serve the iolanta.tech site.

    The site will be available at http://localhost:9841
    """
    sh.mkdocs.serve(
        "-a",
        "localhost:6451",
        _fg=True,
    )


def ci():
    """Run pytest and save the results to artifacts directory."""
    # flakeheaven.call(Path(__file__).parent)

    artifacts.mkdir(parents=True, exist_ok=True)

    sh.pytest.bake(
        color="no",
        junitxml=pytest_xml,
        cov_report="term-missing:skip-covered",
        cov="iolanta",
    ).tests(
        _out=artifacts / "coverage.txt",
    )

    output, pr_count = _mypy_errors_count()

    baseline_file = artifacts / "mypy_baseline.json"
    if baseline_file.exists():
        baseline = json.loads(baseline_file.read_text())
        baseline_count = baseline.get("count", 0)
        console.print(
            f"PR mypy errors: {pr_count}, master baseline: {baseline_count}",
        )
        if pr_count > baseline_count:
            raise ValueError("Mypy error count increased")
    else:
        console.print(f"No master baseline found; PR mypy errors: {pr_count}")


def _mypy_errors_count() -> tuple[str, int]:
    """Run mypy and count its errors."""
    try:
        sh.poetry.run.mypy(
            project_directory,
            *construct_mypy_flags(),
        )
    except sh.ErrorReturnCode as error:
        output = error.stdout.decode("utf-8")
        return output, funcy.ilen(
            line for line in output.splitlines() if "error" in line
        )

    return "", 0


def master():
    """Run the CI pipeline on master."""
    deploy_to_github_pages()

    _output, count = _mypy_errors_count()
    artifacts.mkdir(parents=True, exist_ok=True)
    (artifacts / "mypy_baseline.json").write_text(
        json.dumps(
            {
                "count": count,
            }
        ),
    )


_SUPPORTED_EXAMPLE_SUFFIXES = {".ttl", ".jsonld", ".rdf", ".yamlld"}


def _load_example_graph(path: Path) -> frozenset:
    """Parse an RDF example file into a frozenset of triples."""
    g = rdflib.Graph()
    match path.suffix:
        case ".ttl":
            g.parse(path, format="turtle")
        case ".jsonld":
            g.parse(path, format="json-ld")
        case ".rdf":
            g.parse(path, format="xml")
        case ".yamlld":
            g.parse(data=json.dumps(yaml_ld.expand(path)), format="json-ld")
    return frozenset(g)


def verify_rdf_examples(
    directory: Path = Path("docs/blog/2026-03-15-more-rdf-mappings"),
):
    """Verify that all RDF example files in a directory yield the same triples."""
    example_files = sorted(
        path
        for path in directory.glob("example.*")
        if path.suffix in _SUPPORTED_EXAMPLE_SUFFIXES
    )

    graphs: dict[str, frozenset] = {}
    for path in example_files:
        triples = _load_example_graph(path)
        graphs[path.name] = triples
        console.print(f"[cyan]{path.name}[/cyan]: {len(triples)} triples")

    if len(graphs) < 2:
        console.print("[yellow]Need at least 2 example files to compare.[/yellow]")
        return

    files = list(graphs.keys())
    reference_name = files[0]
    reference_triples = graphs[reference_name]
    all_match = True

    for other_name in files[1:]:
        other_triples = graphs[other_name]
        only_in_ref = reference_triples - other_triples
        only_in_other = other_triples - reference_triples

        if only_in_ref or only_in_other:
            all_match = False
            console.print(f"\n[red]✗ {reference_name} ≠ {other_name}[/red]")
            for triple in sorted(only_in_ref, key=str):
                console.print(f"  [red]only in {reference_name}:[/red] {triple}")
            for triple in sorted(only_in_other, key=str):
                console.print(f"  [red]only in {other_name}:[/red] {triple}")
        else:
            console.print(f"[green]✓[/green] {reference_name} == {other_name}")

    if all_match:
        console.print("\n[bold green]All examples match![/bold green]")
    else:
        raise SystemExit(1)


def dump_pyld_output(source: Path, target: Path):
    """Run `pyld to-rdf` on a file and write the raw output to a file."""
    result = sh.pyld.bake(
        _env={**os.environ, "NO_COLOR": "1"},
    )(
        "to-rdf",
        source,
        _err_to_out=True,
        _ok_code=frozenset((0, 1)),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_ANSI_ESCAPE_PATTERN.sub("", str(result)))
    console.print(f"[green]Written[/green] {target}")


def _dump_iolanta_output(
    source: Path,
    target: Path,
    output_datatype: str = "mermaid",
):
    """Run `iolanta --as` on a file and write the raw output to a file."""
    result = sh.iolanta.bake(
        _env={
            **os.environ,
            "NO_COLOR": "1",
            "XDG_STATE_HOME": "/tmp",
        },
    )(
        source,
        "--as",
        output_datatype,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(str(result))
    console.print(f"[green]Written[/green] {target}")


_REPO_ROOT = project_directory.parent
_REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR = (
    _REPO_ROOT / "docs/blog/remote-contexts-considered-harmful"
)
_ROADMAP_MERMAID = "https://iolanta.tech/roadmap/datatypes/mermaid"


@dataclass(frozen=True)
class DocsMermaidArtifact:
    """Source file, generated `.mmd` target, and Iolanta output datatype."""

    source: Path
    target: Path
    output_datatype: str = "mermaid"


DOCS_MERMAID_ARTIFACTS: tuple[DocsMermaidArtifact, ...] = (
    DocsMermaidArtifact(
        _REPO_ROOT / "docs/mermaid/rdf-example.yamlld",
        _REPO_ROOT / "docs/mermaid/rdf-example.mmd",
        "mermaid/rdf",
    ),
    DocsMermaidArtifact(
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "john-lennon.yamlld",
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "john-lennon.mmd",
    ),
    DocsMermaidArtifact(
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "john-lennon-inline-context.yamlld",
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "john-lennon-inline-context.mmd",
    ),
    DocsMermaidArtifact(
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "index.md",
        _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR / "index.mmd",
    ),
    DocsMermaidArtifact(
        _REPO_ROOT / "docs/roadmap/iolanta-development-roadmap.yamlld",
        _REPO_ROOT / "docs/roadmap/roadmap.mmd",
        _ROADMAP_MERMAID,
    ),
)


def generate_docs_mermaid():
    """Regenerate all committed `.mmd` files included by MkDocs snippets.

    Artifacts:
    - docs/mermaid/rdf-example.mmd (from rdf-example.yamlld, mermaid/rdf)
    - docs/blog/remote-contexts-considered-harmful/john-lennon.mmd
    - docs/blog/remote-contexts-considered-harmful/john-lennon-inline-context.mmd
    - docs/blog/remote-contexts-considered-harmful/index.mmd
    - docs/roadmap/roadmap.mmd (from iolanta-development-roadmap.yamlld)
    """
    with ThreadPoolExecutor() as executor:
        futures = (
            executor.submit(
                _dump_iolanta_output,
                artifact.source,
                artifact.target,
                artifact.output_datatype,
            )
            for artifact in DOCS_MERMAID_ARTIFACTS
        )
        for future in futures:
            future.result()


def generate_remote_contexts_considered_harmful_artifacts():
    """Regenerate all derived outputs for `remote-contexts-considered-harmful`."""
    directory = _REMOTE_CONTEXTS_CONSIDERED_HARMFUL_DIR

    pyld_tasks = (
        lambda: dump_pyld_output(
            directory / "john-lennon-protected.yamlld",
            directory / "john-lennon-protected-result.txt",
        ),
        lambda: dump_pyld_output(
            directory / "john-lennon-sri.jsonld",
            directory / "john-lennon-sri-result.txt",
        ),
        lambda: dump_pyld_output(
            directory / "john-lennon-content-addressed.yamlld",
            directory / "john-lennon-content-addressed-result.txt",
        ),
    )

    with ThreadPoolExecutor() as executor:
        pyld_futures = (executor.submit(task) for task in pyld_tasks)
        mermaid_future = executor.submit(generate_docs_mermaid)
        for future in (*pyld_futures, mermaid_future):
            future.result()


_TRUSTED_DOMAINS = frozenset(
    (
        "w3.org",
        "xmlns.com",
        "schema.org",
        "schemas.org",
    )
)


def sync_prefix_cc():
    """Fetch prefix.cc/context and regenerate iolanta/data/prefixes.yamlld."""
    response = requests.get("http://prefix.cc/context")
    response.raise_for_status()
    context = response.json()["@context"]

    entries = [
        {
            "vann:preferredNamespacePrefix": prefix,
            "vann:preferredNamespaceUri": namespace_url,
        }
        for prefix, namespace_url in sorted(context.items())
        if isinstance(namespace_url, str)
        and len(prefix) >= 2
        and any(domain in namespace_url for domain in _TRUSTED_DOMAINS)
    ]

    (project_directory.parent / "iolanta/data/prefixes.yamlld").write_text(
        yaml.dump(
            {"@context": "context.yaml", "$graph": entries},
            allow_unicode=True,
            sort_keys=False,
        ),
    )
    console.print(f"[green]Written {len(entries)} prefixes[/green]")


def refresh_search_fixtures(notion: str = "Isaac Asimov"):
    """Recapture the four search-resolver fixtures from live APIs.

    Manual command. Not run in CI. Use this when an upstream API contract drift
    is suspected and the captured fixtures need refreshing.
    """
    fixtures_dir = project_directory.parent / "tests/search/fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers["User-Agent"] = "iolanta-fixture-refresh"

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

        sparql_query = (
            "PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>\n"
            "SELECT DISTINCT ?subj ?score WHERE {\n"
            "  ?subj search:matches [\n"
            f'    search:query "{notion}" ;\n'
            "    search:score ?score\n"
            "  ] .\n"
            "} ORDER BY DESC(?score) LIMIT 10"
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
