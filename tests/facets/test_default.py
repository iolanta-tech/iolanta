import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDFS, XSD

from iolanta.facets.cli.default import Default
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
    return "Bazinga"


@pytest.fixture()
def comment() -> str:
    return "Bazingarium"


@pytest.fixture()
def with_label(label: str):
    return {
        "$id": "test",
        "rdfs:label": label,
    }


@pytest.fixture()
def with_label_and_icon(with_label):
    return {
        **with_label,
        "iolanta:icon": "↔",
    }


@pytest.fixture()
def with_label_and_html_icon(with_label):
    return {
        **with_label,
        "iolanta:icon": "<span>↔</span>",
        "rdfs:comment": "foo",
    }


@pytest.fixture()
def with_label_and_comment(with_label, comment: str):
    return {
        **with_label,
        "rdfs:comment": comment,
    }


@pytest.fixture()
def url() -> str:
    return "https://bazinga.com"


@pytest.fixture()
def with_url(with_label, url: str):
    return {
        **with_label,
        "schema:url": url,
    }


@pytest.fixture()
def node() -> URIRef:
    return LOCAL.test


def test_icon_is_rendered_before_label(label: str, node: URIRef):
    iolanta = Iolanta()
    iolanta.graph.add((node, RDFS.label, Literal(label)))
    iolanta.graph.add((node, IOLANTA.icon, Literal("⇔")))

    rendered_label = Default(
        this=node,
        iolanta=iolanta,
        as_datatype=IOLANTA["cli/link"],
    ).render_label()

    assert "⇔" in rendered_label
    assert rendered_label.endswith(f" {label}")


def test_symbol_is_not_rendered_before_label(label: str, node: URIRef):
    iolanta = Iolanta()
    iolanta.graph.add((node, RDFS.label, Literal(label)))
    iolanta.graph.add((node, IOLANTA.symbol, Literal("⇔")))

    rendered_label = Default(
        this=node,
        iolanta=iolanta,
        as_datatype=IOLANTA["cli/link"],
    ).render_label()

    assert rendered_label == label


def test_icon_subproperty_of_p487():
    iolanta = Iolanta()

    assert (
        IOLANTA.icon,
        RDFS.subPropertyOf,
        URIRef("http://www.wikidata.org/prop/direct/P487"),
    ) in iolanta.graph


@pytest.mark.parametrize(
    ("term", "icon"),
    (
        (IOLANTA["is-preferred-over"], "≼"),
        (IOLANTA.outputs, "→"),
        (IOLANTA["when-no-facet-found"], "📛"),
        (IOLANTA.icon, "🖼️"),
        (URIRef("https://iolanta.tech/datatypes/icon"), "🖼️"),
    ),
)
def test_iolanta_terms_have_icons(term: URIRef, icon: str):
    iolanta = Iolanta()

    assert (term, IOLANTA.icon, Literal(icon, datatype=XSD.string)) in iolanta.graph
