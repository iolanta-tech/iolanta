import json

from pydantic import AnyUrl

from iolanta.app import execute_lens


def test_lens():
    response = execute_lens(
        iri='http://www.w3.org/2000/01/rdf-schema#',
        via='https://iolanta.tech/rdfs',
    )

    raise Exception(json.dumps(response, indent=4))
