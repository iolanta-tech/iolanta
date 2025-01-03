from rdflib import URIRef

from iolanta.iolanta import Iolanta


def test_schema_org():
    rows = Iolanta().add({
        '@context': 'https://schema.org',
        '@id': 'johndoe',
        '@type': 'Person',
    }).query('select ?type where { local:johndoe a ?type }')

    row, = rows
    assert row['type'] == URIRef('https://schema.org/Person')
