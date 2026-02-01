"""Pydantic models for kglint report output."""

from enum import StrEnum
from typing import Annotated, Literal as LiteralType

from pydantic import BaseModel, Field


class AssertionCode(StrEnum):
    """Deterministic assertion codes emitted by the linter."""

    LITERAL_LOOKS_LIKE_URI = 'literal-looks-like-uri'
    LITERAL_LOOKS_LIKE_QNAME = 'literal-looks-like-qname'
    URI_LABEL_IDENTICAL = 'uri-label-identical'
    BLANK_LABEL_IDENTICAL = 'blank-label-identical'


class NodeLiteral(BaseModel):
    """Literal term as object: value, datatype, language."""

    type: LiteralType['literal'] = 'literal'
    value: str
    datatype: str | None = None
    language: str | None = None


class NodeURI(BaseModel):
    """URI term as object: value and rendered label."""

    type: LiteralType['uri'] = 'uri'
    value: str
    label: str


class NodeBlank(BaseModel):
    """Blank node term as object: value and rendered label."""

    type: LiteralType['blank'] = 'blank'
    value: str
    label: str


NodeObject = Annotated[
    NodeLiteral | NodeURI | NodeBlank,
    Field(discriminator='type'),
]


class TripleRef(BaseModel):
    """A triple (s, p, o as node objects). Used in assertions and label entries."""

    type: LiteralType['triple'] = 'triple'
    s: NodeObject
    p: NodeObject
    o: NodeObject


class Assertion(BaseModel):
    """Single validation assertion (error or warning)."""

    severity: LiteralType['error', 'warning']
    code: AssertionCode
    target: NodeURI | NodeBlank | TripleRef
    message: str


class LabelEntry(BaseModel):
    """URI/blank node (as object with type, value, label) and participating triples."""

    node: NodeURI | NodeBlank
    triples: list[TripleRef] = Field(default_factory=list)




class Report(BaseModel):
    """KGLint report: assertions and labels."""

    assertions: list[Assertion] = Field(default_factory=list)
    labels: list[LabelEntry] = Field(default_factory=list)
