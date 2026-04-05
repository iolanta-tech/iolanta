from __future__ import annotations

import enum
import hashlib
import re
import textwrap
from urllib import parse as urllib_parse

from documented import Documented
from pydantic import AnyUrl, BaseModel
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import XSD

from iolanta.models import NotLiteralNode  # noqa: WPS202

DATATYPE_ICONS: dict[URIRef, str] = {
    XSD.date: "📅",
    XSD.dateTime: "🕐",
    XSD.boolean: "✅",
}


def escape_label(label: str) -> str:
    """Escape a label and return it wrapped in appropriate quotes.

    Returns the label with URLs stripped, quotes escaped, and wrapped in quotes.
    Uses single quotes if label contains double quotes to avoid escaping issues.

    Escapes quotes in labels that will be wrapped in quotes in Mermaid syntax.
    """
    # Remove https://, http://, and www. prefixes to prevent markdown link parsing
    safe_label = (
        label.replace("https://", "").replace("http://", "").replace("www.", "")
    )
    # Use single quotes if label contains double quotes to avoid escaping issues
    use_single = '"' in safe_label
    quote_char = "'" if use_single else '"'
    # Escape the quote character that will be used for wrapping
    if use_single:
        escaped_label = safe_label.replace("'", r"\'")
    else:
        escaped_label = safe_label.replace('"', r"\"")
    return f"{quote_char}{escaped_label}{quote_char}"


class Direction(enum.StrEnum):
    """Mermaid diagram direction."""

    TB = "TB"
    LR = "LR"


class MermaidScalar(Documented, BaseModel, arbitrary_types_allowed=True):
    """Base class for Mermaid scalar elements (nodes and edges)."""

    @property
    def id(self) -> str:
        """Get the unique identifier for this Mermaid element."""
        raise NotImplementedError()


class MermaidAnchorNode(MermaidScalar, frozen=True):
    """
    {self.id}[" "]
    class {self.id} hidden
    """

    name: str

    @property
    def id(self) -> str:
        name_hash = hashlib.md5(self.name.encode()).hexdigest()
        return f"Anchor_{name_hash}"


class MermaidTextNode(MermaidScalar, frozen=True):
    """
    {self.id}[{self.escaped_title}]
    {self.click_line}
    """

    name: str
    title: str
    url: AnyUrl | None = None

    @property
    def id(self) -> str:
        name_hash = hashlib.md5(self.name.encode()).hexdigest()
        return f"Text_{name_hash}"

    @property
    def escaped_title(self) -> str:
        return escape_label(self.title)

    @property
    def click_line(self) -> str:
        if self.url is None:
            return ""
        return f'click {self.id} "{self.url}"'


class MermaidLabelNode(MermaidScalar, frozen=True):
    """
    {self.id}[{self.escaped_title}]
    class {self.id} label
    {self.click_line}
    """

    name: str
    title: str
    url: AnyUrl | None = None

    @property
    def id(self) -> str:
        name_hash = hashlib.md5(self.name.encode()).hexdigest()
        return f"Label_{name_hash}"

    @property
    def escaped_title(self) -> str:
        return escape_label(self.title)

    @property
    def click_line(self) -> str:
        if self.url is None:
            return ""
        return f'click {self.id} "{self.url}"'


class MermaidHTMLNode(MermaidScalar, frozen=True):
    """
    {self.id}["{self.html}"]
    """

    name: str
    html: str

    @property
    def id(self) -> str:
        name_hash = hashlib.md5(self.name.encode()).hexdigest()
        return f"Html_{name_hash}"


class MermaidDotNode(MermaidScalar, frozen=True):
    """
    {self.id}(" ")
    class {self.id} nanopubdot
    """

    name: str

    @property
    def id(self) -> str:
        name_hash = hashlib.md5(self.name.encode()).hexdigest()
        return f"Dot_{name_hash}"


class MermaidURINode(MermaidScalar, frozen=True):
    """
    {self.id}{self.maybe_title}
    click {self.id} "{self.url}"
    """

    uri: URIRef
    url: AnyUrl
    title: str = ""

    @property
    def maybe_title(self):
        if not self.title:
            return ""
        quoted_title = escape_label(self.title)
        return f"({quoted_title})"

    @property
    def id(self):
        return re.sub(
            r"[:\/\.#()?=&+]", "_", urllib_parse.unquote(str(self.url)).strip("/")
        )


class MermaidLiteral(MermaidScalar, frozen=True):
    """{self.id}[["{self.title}"]]"""

    literal: Literal

    @property
    def title(self) -> str:
        raw_title = str(self.literal) or "EMPTY"
        icon = DATATYPE_ICONS.get(self.literal.datatype, "")
        if icon:
            raw_title = f"{icon} {raw_title}"
        return raw_title.replace('"', "\u201c").replace("'", "\u2019")

    @property
    def id(self) -> str:
        # Use the lexical form of the literal, not rdflib's .value (which may be empty for typed literals),
        # to ensure different texts get distinct node IDs in Mermaid.
        value_hash = hashlib.md5(str(self.literal).encode()).hexdigest()
        return f"Literal-{value_hash}"


class MermaidBlankNode(MermaidScalar):
    """{self.id}({self.escaped_title})"""

    node: BNode
    title: str

    @property
    def id(self) -> str:
        return self.node.replace("_:", "")

    @property
    def escaped_title(self) -> str:
        """Escape the title to prevent Mermaid parsing issues."""
        return escape_label(self.title)


class MermaidEdge(MermaidScalar):
    """
    {self.source.id} --- {self.id}([{self.escaped_title}])--> {self.target.id}
    click {self.id} "{self.predicate}"
    class {self.id} predicate
    """

    source: MermaidScalar | MermaidSubgraph
    target: MermaidScalar | MermaidSubgraph
    predicate: URIRef
    title: str

    @property
    def id(self) -> str:
        return hashlib.md5(
            f"{self.source.id}{self.predicate}{self.target.id}".encode()  # noqa: WPS237
        ).hexdigest()

    @property
    def nodes(self):
        return [self.source, self.target]

    @property
    def escaped_title(self) -> str:
        # Escape URLs to prevent Mermaid from interpreting them as markdown links
        return escape_label(self.title)


class MermaidPlainEdge(MermaidScalar):
    """{self.source.id} --- {self.target.id}"""

    source: MermaidScalar | MermaidSubgraph
    target: MermaidScalar | MermaidSubgraph

    @property
    def id(self) -> str:
        return hashlib.md5(
            f"{self.source.id}{self.target.id}".encode(),
        ).hexdigest()

    @property
    def nodes(self):
        return [self.source, self.target]


class MermaidInvisibleEdge(MermaidScalar):
    """{self.source.id} ~~~ {self.target.id}"""

    source: MermaidScalar | MermaidSubgraph
    target: MermaidScalar | MermaidSubgraph

    @property
    def id(self) -> str:
        return hashlib.md5(
            f"{self.source.id}{self.target.id}invisible".encode(),
        ).hexdigest()

    @property
    def nodes(self):
        return [self.source, self.target]


class MermaidArrowEdge(MermaidScalar):
    """{self.source.id} --> {self.target.id}"""

    source: MermaidScalar | MermaidSubgraph
    target: MermaidScalar | MermaidSubgraph

    @property
    def id(self) -> str:
        return hashlib.md5(
            f"{self.source.id}{self.target.id}arrow".encode(),
        ).hexdigest()

    @property
    def nodes(self):
        return [self.source, self.target]


class MermaidSubgraph(Documented, BaseModel, arbitrary_types_allowed=True, frozen=True):
    """
    subgraph {self.id}{self.maybe_title}
      direction {self.direction}
      {self.formatted_body}
    end
    """

    children: list[MermaidScalar | MermaidSubgraph]
    uri: NotLiteralNode
    title: str | None
    direction: Direction = Direction.LR

    @property
    def id(self):
        uri_hash = hashlib.md5(str(self.uri).encode()).hexdigest()
        return f"subgraph_{uri_hash}"

    @property
    def escaped_title(self) -> str:
        """Escape the subgraph title to prevent markdown link parsing."""
        return "" if self.title is None else escape_label(self.title)

    @property
    def maybe_title(self) -> str:
        if self.title is None:
            return ""
        return f"[{self.escaped_title}]"

    @property
    def formatted_body(self):
        return textwrap.indent(
            "\n".join(map(str, self.children)),
            prefix="  ",
        )


class Diagram(Documented, BaseModel):
    """
    graph {self.direction}
    {self.formatted_body}
      classDef predicate fill:#1f2233,stroke:transparent,color:#f8fafc,stroke-width:0px;
      classDef hidden fill:transparent,stroke:transparent,color:transparent,stroke-width:0px;
      classDef label fill:transparent,stroke:transparent,color:#e5e7eb,stroke-width:0px;
      classDef nanopubdot fill:#0f172a,stroke:#0f172a,color:transparent,stroke-width:2px;
      classDef transparent fill:transparent,stroke:transparent,color:transparent,stroke-width:0px;
      {self.formatted_tail}
    """

    children: list[MermaidScalar | MermaidSubgraph]
    direction: Direction = Direction.LR
    tail: str | None = None

    @property
    def formatted_tail(self) -> str:
        return self.tail or ""

    @property
    def formatted_body(self):
        return textwrap.indent(
            "\n".join(map(str, self.children)),
            prefix="  ",
        )
