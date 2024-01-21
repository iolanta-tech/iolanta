from dataclasses import dataclass

from rdflib import Graph, URIRef, Variable, RDF, ConjunctiveGraph
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Processor
from rdflib.term import Node


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

            try:
                triples = query.algebra['p']['p']['triples']
            except KeyError:
                raise ValueError(query.algebra)

            for triple in triples:
                self.load_data_for_triple(triple, bindings=initBindings)
        else:
            query = strOrQuery
        return evalQuery(self.graph, query, initBindings, base)

    def load_data_for_triple(
        self,
        triple: list[Variable | URIRef],
        bindings: dict[str, Node],
    ):
        """Load data for a given triple."""
        triple = [
            self.resolve_term(term, bindings=bindings)
            for term in triple
        ]

        subject, *_etc = triple

        if isinstance(subject, URIRef):
            if subject in RDF:
                try:
                    self.graph.get_graph(RDF)
                except IndexError:
                    print('DOWNLOADING RDF')
                    self.graph.parse(
                        source=URIRef(RDF),
                        publicID=URIRef(RDF),
                    )

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term
