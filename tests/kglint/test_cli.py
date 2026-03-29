"""CLI alias test for kglint/json."""

import functools
import json
from pathlib import Path

import pytest
import yaml_ld
from rdflib import URIRef
from typer.testing import CliRunner
from yaml_ld.errors import NoLinkedDataFoundInHTML

from iolanta.cli import main as cli_main
from iolanta.cli.main import app
from iolanta.cli.main import render_and_return
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


@pytest.fixture(autouse=True)
def writable_log_path(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cli_main.platformdirs,
        "user_log_path",
        lambda *args, **kwargs: tmp_path,
    )


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


def test_cli_missing_ld(monkeypatch):
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
