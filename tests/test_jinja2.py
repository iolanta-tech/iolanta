import pytest

from iolanta.iolanta import Iolanta
from iolanta_jinja2.process_template import process_template


@pytest.fixture()
def iolanta() -> Iolanta:
    iolanta = Iolanta()
    iolanta.add({
        '@id': 'john-doe',
        'name': 'John Doe',
    })


def test_simple(iolanta: Iolanta):
    assert process_template(
        template='Hi {{ render("name") }}!',
        iolanta=iolanta,
    ) == 'Hi John Doe!'
