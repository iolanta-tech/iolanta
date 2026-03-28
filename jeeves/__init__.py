# noqa: WPS412, WPS400
import json
import os
from pathlib import Path

import funcy
import rdflib
import sh
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
