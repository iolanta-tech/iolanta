from pathlib import Path
from typing import Annotated, Iterable
from typing import Literal as TypingLiteral

from pydantic import (
    AnyUrl,
    BaseModel,
    Field,
    TypeAdapter,
    field_serializer,
    field_validator,
    validator,
)
from rdflib import BNode, Literal, Node, URIRef

from iolanta import Facet
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES


class WithFeedback(BaseModel):
    feedback: Annotated[list[str], Field(default_factory=list)]


class LabeledURI(WithFeedback, BaseModel):
    type: TypingLiteral['uri'] = 'uri'
    uri: AnyUrl
    label: str

    def construct_feedback(self) -> Iterable[str]:
        if str(self.label) == str(self.uri):
            yield (
                'For this URI, the label is the same as the URI. We were '
                'unable to render that URI.'
            )


class LabeledBlank(WithFeedback, BaseModel):
    type: TypingLiteral['blank'] = 'blank'
    identifier: str
    label: str


class LabeledLiteral(WithFeedback, BaseModel):
    type: TypingLiteral['literal'] = 'literal'
    value: str
    language: str | None
    datatype: str | None
    label: str


class LabeledTriple(BaseModel):
    subject: LabeledURI | LabeledBlank
    predicate: LabeledURI
    object_: LabeledURI | LabeledBlank | LabeledLiteral


def construct_uri_feedback(uri: AnyUrl, label: str) -> Iterable[str]:
    if str(uri) == str(label):
        yield (
            'For this URI, the label is the same as the URI. We were '
            'unable to render that URI.'
        )


def construct_blank_feedback(bnode, label) -> Iterable[str]:
    if str(bnode) == str(label):
        yield (
            'For this blank node, the label is the same as the blank node. '
            'We were unable to render that blank node.'
        )


def construct_literal_feedback(literal, label):
    if label.startswith('http'):
        yield (
            'This RDF literal seems to be actually a URL. Good chance is '
            'that it should not be a literal.'
        )
    
    elif ':' in label[:5]:
        yield (
            'This RDF literal seems to be actually a QName (prefixed URI). '
            'Good chance is that it should not be a literal.'
        )


class LabeledTripleSet(Facet[list[LabeledTriple]]):
    """A set of labeled triples."""

    META = Path(__file__).parent / 'data' / 'labeled_triple_set.yamlld'

    def render_label(self, node: NotLiteralNode) -> str:
        return self.render(node, as_datatype=DATATYPES.title)

    def parse_term(self, term: Node):
        match term:
            case URIRef() as uriref:
                uri = AnyUrl(uriref)
                label = self.render_label(uriref)

                return LabeledURI(
                    uri=uri,
                    label=label,
                    feedback=list(construct_uri_feedback(uri=uri, label=label)),
                )

            case BNode() as bnode:
                label = self.render_label(bnode)
                return LabeledBlank(
                    identifier=bnode,
                    label=label,
                    feedback=list(construct_blank_feedback(bnode=bnode, label=label)),
                )

            case Literal() as literal:
                label = self.render_label(literal)
                return LabeledLiteral(
                    value=literal,
                    language=literal.language,
                    datatype=literal.datatype,
                    label=label,
                    feedback=list(construct_literal_feedback(literal=literal, label=label)),
                )

    def show(self):
        rows = self.stored_query('triples.sparql', graph=self.this)
        triples = [
            LabeledTriple(
                subject=self.parse_term(row['subject']),
                predicate=self.parse_term(row['predicate']),
                object_=self.parse_term(row['object']),
            )
            for row in rows
        ]

        return TypeAdapter(list[LabeledTriple]).dump_json(triples, indent=2).decode()
