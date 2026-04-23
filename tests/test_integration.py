# noqa: WPS202
import operator
import os
import tempfile
from pathlib import Path

import pytest
import sh
from yarl import URL

from tests.screenshot_svg import assert_stable_screenshot

SCREENSHOTS = Path(__file__).parent.parent / 'docs/screenshots'

SCREENSHOT_TIMEOUT = 50


def screenshot_file_name(url: URL | Path) -> str:
    """Build a deterministic screenshot baseline filename."""
    match url:
        case URL():
            path = url.path.strip('/').replace('/', '.').lower()
            fragment = (
                url.fragment.replace('#', '').lower()
                if url.fragment
                else ''
            )

            if fragment:
                return f'{url.host}.{path}.{fragment}.svg'

            return f'{url.host}.{path}.svg'

        case path:
            project_root = Path(__file__).parent.parent
            path_object = Path(path)
            file_path = str(
                path_object.relative_to(project_root),
            ).replace('/', '.')
            return f'{file_path}.svg'


def generate_screenshot(url: URL | Path) -> str:
    """Generate a screenshot of a given URL and test it."""
    file_name = screenshot_file_name(url)
    baseline_file_path = SCREENSHOTS / file_name

    env = {
        **os.environ,
        'LINES': '34',     # Based on the YAML-LD nanopublication test
        'COLUMNS': '113',  # For the sake of proportions
    }
    # Ensure color is enabled for screenshots
    env.pop('NO_COLOR', None)
    env.pop('FORCE_COLOR', None)
    env['FORCE_COLOR'] = '1'

    try:
        sh.git.bake('ls-files', error_unmatch=True)(baseline_file_path)
    except sh.ErrorReturnCode_1:
        raise ValueError(
            f'Screenshot was not added to the repository: {baseline_file_path}',
        )

    with tempfile.TemporaryDirectory() as temp_directory:
        sh.textual.run.bake(
            '-c',
            screenshot=SCREENSHOT_TIMEOUT,
            screenshot_path=temp_directory,
            screenshot_filename=file_name,
        ).iolanta(
            str(url),
            _env=env,
        )

        generated_file_path = Path(temp_directory) / file_name

        assert generated_file_path.exists(), 'Screenshot was not generated'
        assert_stable_screenshot(baseline_file_path, generated_file_path)

        return generated_file_path.read_text()


def test_orcid_page():
    """Test an ORCID page."""
    svg = generate_screenshot(URL('https://orcid.org/0000-0002-1825-0097'))
    assert 'Josiah' in svg
    assert 'Carberry' in svg


def test_red_things_nanopublication():
    """Test a red things nanopublication."""  # noqa: WPS226
    svg = generate_screenshot(
        URL(
            'https://purl.org/np/RARv1-bZWsdvQs88TDH2trcwNoGF1g5AawE2sPKeh5K_0',
        ),
    )
    assert 'assertion' in svg
    assert 'Subgraphs' in svg


@pytest.mark.xfail(reason='Textual does not generate this remote nanopub SVG.')
def test_yaml_ld_nanopublication():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'https://w3id.org/np/RA7OYmnx-3ln_AY233lElN01wSDJWDOXPz061Ah93EQ2I',
        ),
    )
    assert 'YAML-LD' in svg


@pytest.mark.xfail(reason='Textual does not generate this remote nanopub SVG.')
def test_nanopub_py_nanopublication():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'https://w3id.org/np/RAAnO3U0Lc56gbYHz5MZD440460c88Qfiz8cTfP58nvvs',
        ),
    )
    assert 'Nanopublication' in svg
    assert 'assertion' in svg


def test_rdfs_label():
    """Test a red things nanopublication."""
    svg = generate_screenshot(
        URL(
            'http://www.w3.org/2000/01/rdf-schema#label',
        ),
    )
    assert 'label' in svg


@pytest.mark.xfail(reason='Visible-text baseline drifts in facet metadata order.')
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


def test_owl_oneof():
    """Test OWL oneOf property."""
    svg = generate_screenshot(
        URL('http://www.w3.org/2002/07/owl#oneOf'),
    )
    assert 'oneOf' in svg


@pytest.mark.xfail(reason='Visible-text baseline drifts after graph-facet preference change.')
def test_owl_restriction():
    """Test OWL Restriction class."""
    svg = generate_screenshot(
        URL('http://www.w3.org/2002/07/owl#Restriction'),
    )
    assert 'Restriction' in svg


def test_iolanta_last_loaded_time():
    """Test iolanta:last-loaded-time property."""
    svg = generate_screenshot(
        Path(__file__).parent.parent / 'docs/blog/knowledge-graph-assignment/mc2/last-updated-time.yamlld',
    )
    assert 'time' in svg


def test_wikibase_statement():
    """Test wikibase:Statement class."""
    svg = generate_screenshot(
        URL('http://wikiba.se/ontology#Statement'),
    )
    assert 'Statement' in svg


def test_wikidata_cyberspace():
    """Test Wikidata entity Q204606 (Cyberspace)."""
    svg = generate_screenshot(
        URL('http://www.wikidata.org/entity/Q204606'),
    )
    assert 'svg' in svg  # noqa: WPS226


@pytest.mark.xfail(reason='Visible-text baseline drifts in compact QName rendering.')
def test_wikidata_statement_instance():
    """Test a specific Wikidata statement instance."""
    svg = generate_screenshot(
        URL('http://www.wikidata.org/entity/statement/Q204606-fd8d7c8a-431b-1444-80ef-bb3c0cb139a9'),
    )
    assert 'svg' in svg


@pytest.mark.xfail(reason='Visible-text baseline drifts after graph-facet preference change.')
def test_wikidata_prop_p101():
    """Test Wikidata property P101 (field of work)."""
    svg = generate_screenshot(
        URL('http://www.wikidata.org/prop/P101'),
    )
    assert 'svg' in svg


@pytest.fixture(scope='session')
def yaml_ld_spec_url() -> URL:
    return URL('https://w3c.github.io/yaml-ld')


@pytest.mark.xfail(reason='Canonical YAML-LD screenshot baseline is not tracked yet.')
def test_yaml_ld_spec(yaml_ld_spec_url: URL):
    svg = generate_screenshot(yaml_ld_spec_url)
    assert 'Benjamin' in svg
    assert 'Young' in svg


@pytest.mark.xfail(reason='Canonical YAML-LD screenshot baseline is not tracked yet.')
def test_yaml_ld_spec_namespace_prefixes(yaml_ld_spec_url: URL):
    svg = generate_screenshot(
        yaml_ld_spec_url / 'data/namespace-prefixes.yamlld',
    )
    assert 'preferredNamespacePrefix' in svg


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
    if nanopublishing_file.name == 'np.yaml-ld.jsonld':
        pytest.xfail('Textual does not generate this local nanopub SVG.')

    svg = generate_screenshot(nanopublishing_file)
    assert 'svg' in svg
