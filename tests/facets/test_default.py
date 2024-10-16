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


def test_fallback(node: URIRef, as_datatype: URIRef):
    assert Iolanta().render(
        node=node,
        as_datatype=as_datatype,
    )[0] == 'Test'


def test_label(with_label, node: URIRef, as_datatype: URIRef, label: str):
    assert Iolanta().add(with_label).render(
        node=node,
        as_datatype=as_datatype,
    )[0] == label


def test_label_and_icon(
    with_label_and_icon,
    node: URIRef,
    as_datatype: URIRef,
    label: str,
):
    assert Iolanta().add(with_label_and_icon).render(
        node=node,
        as_datatype=as_datatype,
    )[0] == '⇔ Bazinga'


def test_label_and_html_icon(
    with_label_and_html_icon,
    node: URIRef,
    as_datatype: URIRef,
    label: str,
    cli: URIRef,
):
    if as_datatype == cli:
        pytest.skip('Not applicable to CLI.')

    assert str(
        Iolanta().add(with_label_and_html_icon).render(
            node=node,
            as_datatype=as_datatype,
        )[0],
    ) == '<span title="foo"><span>⇔</span> Bazinga</span>'


def test_html_comment(
    with_label_and_comment,
    node: URIRef,
    html: URIRef,
    label: str,
    comment: str,
):
    assert Iolanta().add(with_label_and_comment).render(
        node=node,
        as_datatype=html,
    )[0].render() == span(label, title=comment).render()


def test_html_url(
    with_url,
    node: URIRef,
    html: URIRef,
    label: str,
    url: str,
):
    assert Iolanta().add(with_url).render(
        node=node,
        as_datatype=html,
    )[0].render() == a(
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
        as_datatype=cli,
    )[0] == Text(label, style=Style(link=url))
