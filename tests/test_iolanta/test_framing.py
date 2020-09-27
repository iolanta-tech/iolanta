import json
from pyld import jsonld

from rdflib import Graph


TURTLE_TEXT = '''
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix local: <http://localhost/> .

rdfs:
    local:ontology <http://www.w3.org/2002/07/owl#Ontology> ;
    rdfs:label "The RDF Schema vocabulary (RDFS)" .

<http://www.w3.org/2002/07/owl#Ontology> rdfs:label "Ontology" .
'''


def test_rdf_to_jsonld():
    """Convert RDF to JSON-LD with root node."""
    g = Graph()
    g.parse(
        data=TURTLE_TEXT,
        format='turtle',
    )

    jsonld_data = json.loads(g.serialize(
        format='json-ld',
        context={
            '@vocab': 'http://www.w3.org/2000/01/rdf-schema#',
        }
    ))

    frame = {
        '@context': {
            '@vocab': 'http://www.w3.org/2000/01/rdf-schema#',
            'ontology': 'http://localhost/ontology',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        },
        '@id': 'http://www.w3.org/2000/01/rdf-schema#',
    }

    jsonld_data = jsonld.frame(jsonld_data, frame)

    actual_data = json.dumps(jsonld_data, indent=2)
    expected_data = json.dumps({
        '@context': {
            '@vocab': 'http://www.w3.org/2000/01/rdf-schema#',
        },
        '@id': 'http://www.w3.org/2000/01/rdf-schema#',
        'label': 'The RDF Schema vocabulary (RDFS)',

        '@type': {
            '@id': 'http://www.w3.org/2002/07/owl#Ontology',
            'label': 'Ontology',
        },
    }, indent=2)

    # assert actual_data == expected_data
    print(actual_data)
    raise Exception()
