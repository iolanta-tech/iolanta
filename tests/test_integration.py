import os
from pathlib import Path

import sh
from yarl import URL

SCREENSHOTS = Path(__file__).parent.parent / 'docs/screenshots'

SCREENSHOT_TIMEOUT = 50


def generate_screenshot(url: URL) -> str:
    """Generate a screenshot of a given URL and test it."""
    path = url.path.strip('/').replace('/', '.').lower()
    file_name = f'{url.host}.{path}.svg'

    sh.textual.run.bake(
        '-c',
        screenshot=SCREENSHOT_TIMEOUT,
        screenshot_path=SCREENSHOTS,
        screenshot_filename=file_name,
    ).iolanta(
        str(url),
        _env={
            **os.environ,
            'LINES': '34',     # Based on the YAML-LD nanopublication test
            'COLUMNS': '113',  # For the sake of proportions
        },
    )

    file_path = SCREENSHOTS / file_name

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
