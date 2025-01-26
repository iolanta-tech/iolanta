import os
from pathlib import Path

import sh
import typer
from jeeves_yeti_pyproject import flakeheaven
from rich.console import Console

gh = sh.gh.bake(_env={**os.environ, 'NO_COLOR': '1'})

artifacts = Path(__file__).parent / 'tests/artifacts'
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

    try:
        sh.pytest.bake(
            color='no',
            junitxml=pytest_xml,
            cov_report='term-missing:skip-covered',
            cov='iolanta',
        ).tests(
            _out=artifacts / 'coverage.txt',
        )
    except sh.ErrorReturnCode as err:
        typer.echo(err)
        typer.echo(err.stdout)
        typer.echo(err.stderr)
