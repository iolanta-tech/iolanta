from pathlib import Path

import rich
import sh


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


def install_graphviz():
    """Install graphviz."""
    sh.sudo('apt-get', 'install', '-y', 'graphviz')


def todo():
    """Print TODOs."""
    rows: str = sh.grep(
        '-oP',
        r'\{# todo: (\K[^#]+) #\}',
        'docs/project/whitepaper/index.md',
    )

    todos = [
        row.replace(' #}', '')
        for row in rows.split('\n')
    ]

    for todo_item in todos:
        if todo_item:
            rich.print(f'▢ {todo_item}')


def serve():
    """
    Serve the iolanta.tech site.

    The site will be available at http://localhost:9841
    """
    sh.mkdocs.serve(
        '-a', 'localhost:6451',
        _fg=True,
    )
