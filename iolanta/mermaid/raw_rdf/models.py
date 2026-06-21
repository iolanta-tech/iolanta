from pydantic import AnyUrl
from rdflib import BNode, Literal, URIRef

from iolanta.mermaid import models as mermaid_models


def _mermaid_display_label(label: str) -> str:
    return label.replace('"', "\u201c").replace("'", "\u2019")


class MermaidRawURINode(mermaid_models.MermaidScalar, frozen=True):
    """
    {self.id}({self.escaped_title})
    {self.click_line}
    """

    uri: URIRef
    title: str

    @property
    def id(self):
        return mermaid_models._uri_to_mermaid_id(AnyUrl(str(self.uri)))

    @property
    def escaped_title(self) -> str:
        return mermaid_models.escape_label(self.title)

    @property
    def click_line(self) -> str:
        return f'click {self.id} "{self.uri}"'


class MermaidRawLiteral(mermaid_models.MermaidScalar, frozen=True):
    """{self.id}[["{self.display_title}"]]"""

    literal: Literal

    @property
    def display_title(self) -> str:
        return _mermaid_display_label(
            mermaid_models.raw_literal_title(self.literal),
        )

    @property
    def id(self) -> str:
        return mermaid_models._validate_mermaid_id(
            "Literal_"
            + mermaid_models._mermaid_stable_short_id(str(self.literal)),
        )


class MermaidRawBlankNode(mermaid_models.MermaidScalar):
    """{self.id}({self.escaped_title})"""

    node: BNode
    title: str

    @property
    def id(self) -> str:
        return mermaid_models._validate_mermaid_id(
            f"B{mermaid_models._mermaid_stable_short_id(str(self.node))}",
        )

    @property
    def escaped_title(self) -> str:
        return mermaid_models.escape_label(
            f"{mermaid_models.BLANK_NODE_ICON} {self.title}",
        )


class MermaidRawEdge(mermaid_models.MermaidScalar):
    """
    {self.source.id} --- {self.id}([{self.escaped_title}])--> {self.target.id}
    {self.click_line}
    """

    source: mermaid_models.MermaidScalar | mermaid_models.MermaidSubgraph
    target: mermaid_models.MermaidScalar | mermaid_models.MermaidSubgraph
    predicate: URIRef
    title: str

    @property
    def id(self) -> str:
        return mermaid_models._validate_mermaid_id(
            mermaid_models._MERMAID_EDGE_ID_PREFIX
            + mermaid_models._mermaid_stable_short_id(
                f"{self.source.id}",
                str(self.predicate),
                f"{self.target.id}",
            ),
        )

    @property
    def nodes(self):
        return [self.source, self.target]

    @property
    def escaped_title(self) -> str:
        return mermaid_models.escape_label(self.title)

    @property
    def click_line(self) -> str:
        return f'click {self.id} "{self.predicate}"'
