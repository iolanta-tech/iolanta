"""CLI alias test for kglint/json."""

import json
from pathlib import Path

import pytest
from click.testing import Result
from rdflib import URIRef
from typer.testing import CliRunner
from yaml_ld.errors import NoLinkedDataFoundInHTML

from iolanta.cli import main as cli_main
from iolanta.cli.main import app, render_and_return
from iolanta.sparqlspace import processor

FIXTURES_DIR = Path(__file__).parent / "data"


def _skip_indices(sparql_processor):
    sparql_processor.graph


def _load_document_with_missing_ld(
    uri,
    *,
    original_load_document,
):
    if str(uri) == "https://example.com/no-ld":
        raise NoLinkedDataFoundInHTML(
            "No linked data fragments found in HTML",
        )
    return original_load_document(uri)


def _raise_read_only_log_path(*args, **kwargs):
    raise OSError("read-only")


def _write_person_data(tmp_path: Path) -> None:
    data_path = tmp_path / "data.yamlld"
    data_path.write_text(
        "\n".join(
            [
                '"@context":',
                "  ex: http://example.org/",
                "  rdfs: http://www.w3.org/2000/01/rdf-schema#",
                "",
                '"@id": ex:Person',
                "rdfs:label: Person",
            ]
        ),
    )


def _write_template(tmp_path, template_text: str) -> Path:
    template_path = tmp_path / "document.jinja2.md"
    template_path.write_text(template_text)
    return template_path


def _invoke_render_template(template_path: Path, *args: str) -> Result:
    runner = CliRunner()
    return runner.invoke(
        app,
        ["--render-template", str(template_path), *args],
    )


@pytest.fixture(autouse=True)
def writable_log_path(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cli_main.platformdirs,
        "user_log_path",
        lambda *args, **kwargs: tmp_path,
    )


def test_setup_logging_uses_temp_fallback(
    monkeypatch,
    tmp_path,
):
    """Sandboxed agents may not be able to write platform user state dirs."""
    monkeypatch.setattr(
        cli_main.platformdirs,
        "user_log_path",
        _raise_read_only_log_path,
    )
    monkeypatch.setattr(
        cli_main.tempfile,
        "gettempdir",
        lambda: str(tmp_path),
    )

    logger = cli_main.setup_logging(cli_main.LogLevel.ERROR)
    logger.error("fallback log test")

    assert (tmp_path / "iolanta/log/iolanta.log").exists()


def test_cli_kglint_json():
    """CLI with --as kglint/json returns valid JSON with assertions and labels."""
    path = (FIXTURES_DIR / "clean.yamlld").resolve()
    node = URIRef(f"file://{path}")
    raw = render_and_return(node=node, as_datatype="kglint/json")
    report = json.loads(raw)
    assert "assertions" in report  # noqa: WPS226
    assert "labels" in report  # noqa: WPS226
    assert isinstance(report["assertions"], list)
    assert isinstance(report["labels"], list)


def test_cli_command_outputs_valid_json():
    runner = CliRunner()
    command_result = runner.invoke(
        app,
        ["tests/kglint/data/clean.yamlld", "--as", "kglint/json"],
    )
    report = json.loads(command_result.stdout)

    assert command_result.exit_code == 0
    assert "assertions" in report  # noqa: WPS226
    assert "labels" in report  # noqa: WPS226


def test_cli_render_template_outputs_markdown(tmp_path):
    _write_person_data(tmp_path)
    template_path = _write_template(
        tmp_path,
        '# {{ URIRef("http://example.org/Person") | as("title") }}',
    )

    command_result = _invoke_render_template(template_path)

    assert command_result.exit_code == 0
    assert command_result.stdout == "# Person\n"


def test_cli_render_template_sparql(tmp_path):
    _write_person_data(tmp_path)
    query_path = tmp_path / "labels.sparql"
    query_path.write_text("SELECT ?label WHERE { $iri rdfs:label ?label . }")
    template_path = _write_template(
        tmp_path,
        '{{ sparql("labels.sparql", iri=URIRef("http://example.org/Person")) }}',
    )

    command_result = _invoke_render_template(template_path)

    assert command_result.exit_code == 0
    assert "| label |" in command_result.stdout
    assert "| `Person` |" in command_result.stdout


@pytest.mark.parametrize(
    "extra_args",
    [
        ("--query", "SELECT * WHERE {}"),
        ("--search", "Person", "--as", "jsonl"),
        ("https://example.org/Person",),
    ],
)
def test_cli_render_template_rejects_other_modes(tmp_path, extra_args):
    template_path = _write_template(tmp_path, "content")

    command_result = _invoke_render_template(
        template_path,
        *extra_args,
    )

    assert command_result.exit_code == 1
    assert "provide only one" in command_result.stdout


def test_cli_render_template_rejects_as(tmp_path):
    template_path = _write_template(tmp_path, "content")

    command_result = _invoke_render_template(template_path, "--as", "title")

    assert command_result.exit_code == 1
    assert "--render-template cannot be combined with --as" in command_result.stdout


def test_cli_missing_ld(monkeypatch):
    import functools

    import yaml_ld

    path = (FIXTURES_DIR / "remote_no_ld.yamlld").resolve()
    node = URIRef(f"file://{path}")
    monkeypatch.setattr(
        processor.GlobalSPARQLProcessor,
        "_maybe_load_indices",
        _skip_indices,
    )
    monkeypatch.setattr(
        processor.yaml_ld,
        "load_document",
        functools.partial(
            _load_document_with_missing_ld,
            original_load_document=yaml_ld.load_document,
        ),
    )

    raw = render_and_return(node=node, as_datatype="kglint/json")
    report = json.loads(raw)

    assert "assertions" in report
    assert "labels" in report


def test_direct_url_without_render_subcommand(monkeypatch):
    called: list[dict] = []

    def fake_render_and_return(**kwargs):
        called.append(kwargs)
        return "ok"

    monkeypatch.setattr(cli_main, "render_and_return", fake_render_and_return)
    monkeypatch.setattr(cli_main, "print_renderable", lambda _renderable: None)

    result = CliRunner().invoke(app, ["rdf:Alt", "--as", "title"])

    assert result.exit_code == 0
    assert called
    assert called[0]["node"] == URIRef("rdf:Alt")


def test_without_visualization_cache_index_flag(monkeypatch):
    called: list[dict] = []

    def fake_render_and_return(**kwargs):
        called.append(kwargs)
        return "ok"

    monkeypatch.setattr(cli_main, "render_and_return", fake_render_and_return)
    monkeypatch.setattr(cli_main, "print_renderable", lambda _renderable: None)

    result = CliRunner().invoke(
        app,
        ["--without-visualization-cache-index", "rdf:Alt", "--as", "title"],
    )

    assert result.exit_code == 0
    assert called[0]["without_visualization_cache_index"] is True
