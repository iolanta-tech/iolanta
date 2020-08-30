import json
from pathlib import Path

from iolanta.app import query_graph


def test_rdfs():
    path = Path(__file__).parent.parent / 'static/iolanta-rdfs.sparql'

    with open(str(path), 'r') as query_file:
        query = query_file.read()

    response = query_graph(query)

    raise Exception(json.dumps(response, indent=2))
