import operator
import os
from pathlib import Path

import pytest
import sh
from yarl import URL

SCREENSHOTS = Path(__file__).parent.parent / 'docs/screenshots'

SCREENSHOT_TIMEOUT = 50


def generate_screenshot(url: URL | Path) -> str:
    """Generate a screenshot of a given URL and test it."""
    match url:
        case URL():
            path = url.path.strip('/').replace('/', '.').lower()
            screenshot_file_name = f'{url.host}.{path}.svg'

        case Path() as path:
            project_root = Path(__file__).parent.parent
            file_path = str(
                path.relative_to(project_root),
            ).replace('/', '.')
            screenshot_file_name = f'{file_path}.svg'

    sh.textual.run.bake(
        '-c',
        screenshot=SCREENSHOT_TIMEOUT,
        screenshot_path=SCREENSHOTS,
        screenshot_filename=screenshot_file_name,
    ).iolanta(
        str(url),
        _env={
            **os.environ,
            'LINES': '34',     # Based on the YAML-LD nanopublication test
            'COLUMNS': '113',  # For the sake of proportions
        },
    )

    file_path = SCREENSHOTS / screenshot_file_name

    assert file_path.exists(), 'Screenshot was not generated'

    try:
        sh.git.bake('ls-files', error_unmatch=True)(file_path)
    except sh.ErrorReturnCode_1:
        raise ValueError(
            f'Screenshot was not added to the repository: {file_path}',
        )

    try:
        sh.git.diff.bake(quiet=True)(file_path)
    except sh.ErrorReturnCode_1:
        raise ValueError(
            f'Screenshot was changed: {file_path}',
        )

    return file_path.read_text()


def test_orcid_page():
    """Test an ORCID page."""
    svg = generate_screenshot(URL('https://orcid.org/0000-0002-1825-0097'))
    assert 'Josiah' in svg
    assert 'Carberry' in svg


def test_red_things_nanopublication():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'https://purl.org/np/RARv1-bZWsdvQs88TDH2trcwNoGF1g5AawE2sPKeh5K_0',
        ),
    )
    assert 'red' in svg
    assert 'things' in svg
    assert 'Class' in svg


def test_yaml_ld_nanopublication():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'https://w3id.org/np/RA7OYmnx-3ln_AY233lElN01wSDJWDOXPz061Ah93EQ2I',
        ),
    )
    assert 'YAML-LD' in svg


def test_nanopub_py_nanopublication():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'https://w3id.org/np/RAAnO3U0Lc56gbYHz5MZD440460c88Qfiz8cTfP58nvvs',
        ),
    )
    assert 'YAML-LD' in svg


def test_rdfs_label():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'http://www.w3.org/2000/01/rdf-schema#label',
        ),
    )
    assert 'label' in svg


def test_rdfg_graph():
    """Test the RDFG Graph class."""
    svg = generate_screenshot(
        URL('http://www.w3.org/2009/rdfg#Graph'),
    )
    assert 'Graph' in svg


def test_meta():
    """Test the RDFG Graph class."""
    svg = generate_screenshot(
        URL('iolanta://_meta'),
    )
    assert 'time' in svg


@pytest.fixture(scope='session')
def yaml_ld_spec_url() -> URL:
    return URL('https://json-ld.github.io/yaml-ld/spec')


def test_yaml_ld_spec(yaml_ld_spec_url: URL):
    svg = generate_screenshot(yaml_ld_spec_url)
    assert 'YAML-LD' in svg


def test_yaml_ld_spec_namespace_prefixes(yaml_ld_spec_url: URL):
    svg = generate_screenshot(
        yaml_ld_spec_url / 'data/namespace-prefixes.yamlld',
    )
    assert 'Prefix' in svg


NANOPUBLISH_DIRECTORY = Path(__file__).parent.parent / 'docs/howto/nanopublish'


@pytest.mark.parametrize(
    'nanopublishing_file',
    [
        *NANOPUBLISH_DIRECTORY.glob('*.yamlld'),
        *NANOPUBLISH_DIRECTORY.glob('*.jsonld'),
    ],
    ids=operator.attrgetter('stem'),
)
def test_nanopublishing(nanopublishing_file: Path):
    svg = generate_screenshot(nanopublishing_file)
    assert 'svg' in svg
