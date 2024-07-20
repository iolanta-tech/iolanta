import dataclasses
import traceback
from dataclasses import dataclass
from typing import Any, ItemsView, Iterable, Mapping

import rdflib_pyld_compat
import yaml_ld
from boltons.iterutils import default_enter, remap
from rdflib import (
    DC,
    FOAF,
    OWL,
    RDF,
    RDFS,
    VANN,
    ConjunctiveGraph,
    Graph,
    Namespace,
    URIRef,
    Variable,
)
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Processor
from rdflib.term import Node
from yaml_ld.errors import NotFound
from yaml_ld.to_rdf import ToRDFOptions

from iolanta.models import Triple, TripleWithVariables
from iolanta.parsers.dict_parser import UnresolvedIRI, parse_quads


def construct_flat_triples(algebra: Mapping[str, Any]) -> Iterable[Triple]:
    if isinstance(algebra, Mapping):
        for key, value in algebra.items():
            if key == 'triples':
                yield from [Triple(*raw_triple) for raw_triple in value]

            else:
                yield from construct_flat_triples(value)


@dataclass
class GlobalSPARQLProcessor(Processor):
    graph: ConjunctiveGraph

    def query(
        self,
        strOrQuery,
        initBindings={},
        initNs={},
        base=None,
        DEBUG=False,
    ):
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """
        if not isinstance(strOrQuery, Query):
            parsetree = parseQuery(strOrQuery)
            query = translateQuery(parsetree, base, initNs)

            triples = construct_flat_triples(query.algebra)
            for triple in triples:
                self.load_data_for_triple(triple, bindings=initBindings)
        else:
            query = strOrQuery
        return evalQuery(self.graph, query, initBindings, base)

    def load(self, source: str):
        if source == str(VANN):
            source = 'https://vocab.org/vann/vann-vocab-20100607.rdf'

        try:
            ld_rdf = yaml_ld.to_rdf(source, options=ToRDFOptions())
        except NotFound as not_found:
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(namespace):
                    return self.load(namespace)

        try:
            self.graph.addN(
                parse_quads(
                    quads_document=ld_rdf,
                    graph=subject,  # type: ignore
                    blank_node_prefix=str(subject),
                ),
            )
            return
        except UnresolvedIRI as err:
            raise dataclasses.replace(
                err,
                context=None,
                iri=source,
            )

    def load_data_for_triple(
        self,
        triple: TripleWithVariables,
        bindings: dict[str, Node],
    ):
        """Load data for a given triple."""
        triple = TripleWithVariables(
            *[
                self.resolve_term(term, bindings=bindings)
                for term in triple
            ],
        )

        subject, *_etc = triple

        if isinstance(subject, URIRef):
            ...

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term
