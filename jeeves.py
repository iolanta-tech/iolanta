import functools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated

import rich
import sh
from rich.console import Console
from typer import Argument

# Screenshot delay.
SCREENSHOT_DELAY = 35

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


def screenshots(iri: Annotated[str | None, Argument()] = None):
    """Generate screenshots."""
    filename_by_iri = {
        'rdfs:': 'rdfs.svg',
        'rdfs:Class': 'rdfs-class.svg',
        'rdf:': 'rdf.svg',
        'rdf:type': 'rdf-type.svg',
        'foaf:': 'foaf.svg',
        'owl:': 'owl.svg',
        'owl:Ontology': 'owl-ontology.svg',
        'vann:': 'vann.svg',
        'http://www.wikidata.org/entity/Q204606': 'wikidata-cyberspace.svg',
    }

    with ThreadPoolExecutor(max_workers=10) as executor:
        for destination, filename in filename_by_iri.items():
            if iri is not None and iri != destination:
                continue

            screenshot_path = Path(__file__).parent / 'docs/screenshots'

            executor.submit(
                functools.partial(
                    sh.textual.run.bake(
                        '-c',
                        screenshot=SCREENSHOT_DELAY,
                        screenshot_path=screenshot_path,
                        screenshot_filename=filename,
                    ).iolanta,
                    destination,
                ),
            )

        executor.shutdown()
