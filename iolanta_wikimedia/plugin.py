from pathlib import Path
from typing import List

import funcy
from rdflib.term import Node
from urlpath import URL

from iolanta import Plugin


class IolantaWikimedia(Plugin):
    """Iolanta integration for Wikimedia projects."""

    def retrieve(self, node: Node) -> List[Path]:
        node_url = URL(node)

        if node_url.hostname != 'dbpedia.org':
            return []

        dynamic_path_part = '{}.json'.format(
            node_url.path.lstrip('/').lower(),
        )
        target_path: Path = (
            self.iolanta.project_directory / 'retrieved/wikimedia/dbpedia.org' /
            dynamic_path_part
        )
        if target_path.exists():
            self.logger.warning(
                '%s already exists, skipping download.', target_path,
            )
            return []

        self.logger.warning('Downloading: %s…', target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            URL('https://dbpedia.org/sparql').with_query({
                'default-graph-uri': 'http://dbpedia.org',
                'query': f'DESCRIBE <{node}>',
                'format': 'application/ld+json',
            }).get_text(),
        )

        return [target_path]
