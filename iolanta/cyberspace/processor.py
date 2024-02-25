import traceback
from dataclasses import dataclass
from typing import ItemsView, Iterable, Mapping, Any

from boltons.iterutils import remap, default_enter
from rdflib import (
    URIRef, Variable, RDF, ConjunctiveGraph, Graph, RDFS, FOAF,
    Namespace, OWL, DC, VANN,
)
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Processor
from rdflib.term import Node

from iolanta.models import Triple, TripleWithVariables


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

    def _download_namespace(self, namespace: Namespace):
        if namespace == VANN:
            iri = URIRef('https://vocab.org/vann/vann-vocab-20100607.rdf')
        else:
            iri = URIRef(namespace)

        try:
            self.graph.get_graph(iri)
        except IndexError:
            print(f'DOWNLOADING {namespace}')
            self.graph.get_context(iri).parse(iri)
            print(f'DOWNLOADED {namespace}!')

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

    def load_data_for_triple(
        self,
        triple: TripleWithVariables,
        bindings: dict[str, Node],
    ):
        """Load data for a given triple."""
        triple = TripleWithVariables(*[
            self.resolve_term(term, bindings=bindings)
            for term in triple
        ])

        subject, *_etc = triple

        if isinstance(subject, URIRef):
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if subject == URIRef(namespace) or subject in namespace:
                    self._download_namespace(namespace)

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term
