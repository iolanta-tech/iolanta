import json
import os
from pathlib import Path

import funcy
import sh
from jeeves_yeti_pyproject import flakeheaven
from jeeves_yeti_pyproject.mypy import construct_mypy_flags
from rich.console import Console

gh = sh.gh.bake(_env={**os.environ, 'NO_COLOR': '1'})

project_directory = Path(__file__).parent
artifacts = project_directory / 'tests/artifacts'
pytest_xml = artifacts / 'pytest.xml'

console = Console()


def install_mkdocs_insiders():
    """Install Insiders version of `mkdocs-material` theme."""
    name = 'mkdocs-material-insiders'

    if not (Path.cwd() / name).is_dir():
        sh.gh.repo.clone(f'iolanta-tech/{name}')

    sh.pip.install('-e', name)


def deploy_to_github_pages():
    """Build the docs & deploy → gh-pages branch."""
    try:
        sh.mkdocs('gh-deploy', '--force', '--clean', '--verbose')
    except sh.ErrorReturnCode as error:
        raise ValueError(error.stderr.decode('utf-8'))


def serve():
    """
    Serve the iolanta.tech site.

    The site will be available at http://localhost:9841
    """
    sh.mkdocs.serve(
        '-a', 'localhost:6451',
        _fg=True,
    )


def ci():
    """Run pytest and save the results to artifacts directory."""
    flakeheaven.call(Path(__file__).parent)

    artifacts.mkdir(parents=True, exist_ok=True)

    sh.pytest.bake(
        color='no',
        junitxml=pytest_xml,
        cov_report='term-missing:skip-covered',
        cov='iolanta',
    ).tests(
        _out=artifacts / 'coverage.txt',
    )

    output, pr_count = _mypy_errors_count()

    baseline_file = artifacts / 'mypy_baseline.json'
    if baseline_file.exists():
        baseline = json.loads(baseline_file.read_text())
        baseline_count = baseline.get('count', 0)
        console.print(
            f'PR mypy errors: {pr_count}, master baseline: {baseline_count}',
        )
        if pr_count > baseline_count:
            raise ValueError('Mypy error count increased')
    else:
        console.print(f'No master baseline found; PR mypy errors: {pr_count}')


def _mypy_errors_count() -> tuple[str, int]:
    """Run mypy and count its errors."""
    try:
        sh.poetry.run.mypy(
            project_directory,
            *construct_mypy_flags(),
        )
    except sh.ErrorReturnCode_2 as error:
        output = error.stdout.decode('utf-8')
        return output, funcy.ilen(
            line
            for line in output.splitlines()
            if 'error' in line
        )

    return '', 0


def master():
    """Run the CI pipeline on master."""
    install_mkdocs_insiders()
    deploy_to_github_pages()

    _output, count = _mypy_errors_count()
    (artifacts / 'mypy_baseline.json').write_text(
        json.dumps({
            'count': count,
        }),
    )
