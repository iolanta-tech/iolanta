from pathlib import Path

import pytest
from rdflib import Literal

from iolanta.iolanta import Iolanta


@pytest.fixture
def data_files() -> Path:
    return Path(__file__).parent / 'data'


def test_braces(iolanta: Iolanta, data_files: Path):
    rows = iolanta.add(
        data_files / 'braces.yaml',
    ).query('SELECT * WHERE { local:test local:title ?title }')

    row, = rows

    assert row['title'] == Literal('Open {page} in web browser')
