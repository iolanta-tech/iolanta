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


def test_fallback(node: URIRef, environment: URIRef):
    assert Iolanta().render(
        node=node,
        environments=[environment],
    ) == 'Test'


def test_label(with_label, node: URIRef, environment: URIRef, label: str):
    assert Iolanta().add(with_label).render(
        node=node,
        environments=[environment],
    ) == label


def test_html_comment(
    with_label_and_comment,
    node: URIRef,
    html: URIRef,
    label: str,
    comment: str,
):
    assert Iolanta().add(with_label_and_comment).render(
        node=node,
        environments=[html],
    ).render() == span(label, title=comment).render()


def test_html_url(
    with_url,
    node: URIRef,
    html: URIRef,
    label: str,
    url: str,
):
    assert Iolanta().add(with_url).render(
        node=node,
        environments=[html],
    ).render() == a(
        label,
        href=url,
    ).render()


def test_cli_url(
    with_url,
    node: URIRef,
    cli: URIRef,
    label: str,
    url: str,
):
    assert Iolanta().add(with_url).render(
        node=node,
        environments=[cli],
    ) == Text(label, style=Style(link=url))
