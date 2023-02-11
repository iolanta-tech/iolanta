import pytest

from iolanta.iolanta import Iolanta
from iolanta_jinja2.process_template import process_template


@pytest.fixture()
def iolanta() -> Iolanta:
    return Iolanta().add({
        '@id': 'john-doe',
        'rdfs:label': 'John Doe',
    })


def test_simple(iolanta: Iolanta):
    assert process_template(
        template='Hi {{ render("john-doe") }}!',
        iolanta=iolanta,
    ) == 'Hi John Doe!'
