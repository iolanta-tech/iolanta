from dominate.tags import span
from rdflib import Literal

from iolanta.iolanta import Iolanta
from iolanta.namespaces import LOCAL


def test_label():
    assert Iolanta().add({
        '@id': 'test',
        'rdfs:label': 'foo',
    }).render(
        LOCAL.test,
    ) == Literal('foo')


def test_comment():
    assert str(
        Iolanta().add({
            '@id': 'test',
            'rdfs:label': 'foo',
            'rdfs:comment': 'boo',
        }).render(
            LOCAL.test,
        ),
    ) == str(
        span(
            'foo',
            title='boo',
        ),
    )
