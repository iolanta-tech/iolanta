from rdflib import URIRef
from rdflib.term import Node
from yarl import URL

from iolanta.models import NotLiteralNode, Triple


class TripleURIRef(URIRef):
    """URN serialization of an RDF triple."""

    @classmethod
    def from_triple(
        cls,
        subject: NotLiteralNode,
        predicate: NotLiteralNode,
        object_: Node,
    ) -> 'TripleURIRef':
        """
        Construct from triple.

        TODO Add special query arguments to conform to RDF standard:
          * subject_bnode
          * predicate_bnode
          * object_bnode
          * object_datatype
          * object_language

        TODO Standardize this?
        """
        iri = URL.build(
            scheme='urn:rdf',
            query={
                'subject': subject,
                'predicate': predicate,
                'object': object_,
            },
        )
        return TripleURIRef(str(iri))

    def as_triple(self) -> Triple:
        """
        Deserialize into a triple.

        TODO support special query arguments described above.
        """
        url = URL(self)
        return Triple(
            subject=URIRef(url.query['subject']),
            predicate=URIRef(url.query['predicate']),
            object=URIRef(url.query['object']),
        )
