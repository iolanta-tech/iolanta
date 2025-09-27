import enum
import hashlib
import re
import textwrap
import urllib.parse


def escape_label(label: str) -> str:
    """Escape a label to prevent Mermaid from interpreting URLs as markdown links."""
    # Remove https://, http://, and www. prefixes to prevent markdown link parsing
    return label.replace('https://', '').replace('http://', '').replace('www.', '')

from documented import Documented
from pydantic import AnyUrl, BaseModel
from rdflib import BNode, Literal, URIRef

from iolanta.models import NotLiteralNode


class Direction(enum.StrEnum):
    """Mermaid diagram direction."""

    TB = 'TB'
    LR = 'LR'


class MermaidURINode(Documented, BaseModel, arbitrary_types_allowed=True, frozen=True):
    """
    {self.id}{self.maybe_title}
    click {self.id} "{self.url}"
    """

    uri: URIRef
    url: AnyUrl
    title: str = ''

    @property
    def maybe_title(self):
        if not self.title:
            return ''
        # Escape URLs to prevent Mermaid from interpreting them as markdown links
        safe_title = escape_label(self.title)
        return f'("{safe_title}")'

    @property
    def id(self):
        return re.sub(r'[:\/\.#()]', '_', urllib.parse.unquote(str(self.url)).strip('/'))


class MermaidLiteral(Documented, BaseModel, arbitrary_types_allowed=True, frozen=True):
    """{self.id}[["{self.title}"]]"""

    literal: Literal

    @property
    def title(self) -> str:
        raw_title = str(self.literal) or 'EMPTY'
        # Replace quotes with safer characters for Mermaid
        return raw_title.replace('"', '"').replace("'", "'")

    @property
    def id(self) -> str:
        value_hash = hashlib.md5(str(self.literal.value).encode()).hexdigest()
        return f'Literal-{value_hash}'


class MermaidBlankNode(Documented, BaseModel, arbitrary_types_allowed=True):
    """{self.id}({self.escaped_title})"""

    node: BNode
    title: str

    @property
    def id(self) -> str:
        return self.node.replace('_:', '')
    
    @property
    def escaped_title(self) -> str:
        return self.title


class MermaidEdge(Documented, BaseModel, arbitrary_types_allowed=True):
    """
    {self.source.id} --- {self.id}(["{self.escaped_title}"])--> {self.target.id}
    click {self.id} "{self.predicate}"
    class {self.id} predicate
    """

    source: 'MermaidURINode | MermaidBlankNode | MermaidSubgraph'
    target: 'MermaidURINode | MermaidLiteral | MermaidBlankNode | MermaidSubgraph'
    predicate: URIRef
    title: str

    @property
    def id(self) -> str:
        return hashlib.md5(f'{self.source.id}{self.predicate}{self.target.id}'.encode()).hexdigest()

    @property
    def nodes(self):
        return [self.source, self.target]
    
    @property
    def escaped_title(self) -> str:
        # Escape URLs to prevent Mermaid from interpreting them as markdown links
        return escape_label(self.title)


MermaidScalar = MermaidLiteral | MermaidBlankNode | MermaidURINode | MermaidEdge


class MermaidSubgraph(Documented, BaseModel, arbitrary_types_allowed=True, frozen=True):
    """
    subgraph {self.id}["{self.escaped_title}"]
      direction {self.direction}
      {self.formatted_body}
    end
    """
    children: list[MermaidScalar]
    uri: NotLiteralNode
    title: str
    direction: Direction = Direction.LR

    @property
    def id(self):
        uri_hash = hashlib.md5(str(self.uri).encode()).hexdigest()
        return f'subgraph_{uri_hash}'
    
    @property
    def escaped_title(self) -> str:
        """Escape the subgraph title to prevent markdown link parsing."""
        return escape_label(self.title)

    @property
    def formatted_body(self):
        return textwrap.indent(
            '\n'.join(map(str, self.children)),
            prefix='  ',
        )


class Diagram(Documented, BaseModel):
    """
    graph {self.direction}
    {self.formatted_body}
      classDef predicate fill:none,stroke:none,stroke-width:0px;
    """

    children: list[MermaidScalar | MermaidSubgraph]
    direction: Direction = Direction.LR

    @property
    def formatted_body(self):
        return textwrap.indent(
            '\n'.join(map(str, self.children)),
            prefix='  ',
        )
