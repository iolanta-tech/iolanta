import pytest
from dominate.tags import a, span
from rdflib import URIRef
from rich.style import Style
from rich.text import Text

from iolanta.iolanta import Iolanta
from iolanta.namespaces import IOLANTA, LOCAL


@pytest.fixture()
def html() -> URIRef:
    return IOLANTA.html


@pytest.fixture()
def cli() -> URIRef:
    return IOLANTA.cli


@pytest.fixture()
def label() -> str:
    return 'Bazinga'


@pytest.fixture()
def comment() -> str:
    return 'Bazingarium'


@pytest.fixture()
def with_label(label: str):
    return {
        '$id': 'test',
        'rdfs:label': label,
    }


@pytest.fixture()
def with_label_and_icon(with_label):
    return {
        **with_label,
        'iolanta:symbol': '⇔',
    }


@pytest.fixture()
def with_label_and_html_icon(with_label):
    return {
        **with_label,
        'iolanta:symbol': '<span>⇔</span>',
        'rdfs:comment': 'foo',
    }


@pytest.fixture()
def with_label_and_comment(with_label, comment: str):
    return {
        **with_label,
        'rdfs:comment': comment,
    }


@pytest.fixture()
def url() -> str:
    return 'https://bazinga.com'


@pytest.fixture()
def with_url(with_label, url: str):
    return {
        **with_label,
        'schema:url': url,
    }


@pytest.fixture()
def node() -> URIRef:
    return LOCAL.test
