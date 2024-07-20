import dataclasses
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import owlrl
import yaml_ld
from rdflib import (
    DC,
    FOAF,
    OWL,
    RDF,
    RDFS,
    VANN,
    ConjunctiveGraph,
    URIRef,
    Variable,
)
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.evaluate import evalQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.sparql import Query
from rdflib.query import Processor
from rdflib.term import Node
from yaml_ld.errors import NotFound
from yaml_ld.to_rdf import ToRDFOptions

from iolanta.models import Triple, TripleWithVariables
from iolanta.parsers.dict_parser import UnresolvedIRI, parse_quads

logger = logging.getLogger(__name__)


REDIRECTS = {
    # FIXME This is presently hardcoded; we need to
    #   - either find a way to resolve these URLs automatically,
    #   - or create a repository of those redirects online.
    'http://purl.org/vocab/vann/': 'https://vocab.org/vann/vann-vocab-20100607.rdf',
}


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

        closure_class = owlrl.OWLRL_Extension
        logger.info(
            'Inference @ cyberspace: %s started...',
            closure_class.__name__,
        )
        owlrl.DeductiveClosure(closure_class).expand(self.graph)
        logger.info('Inference @ cyberspace: complete.')

        return evalQuery(self.graph, query, initBindings, base)

    def load(self, source: str):
        if source.startswith('file://') or source.startswith('python://'):
            # FIXME temporary fix. `yaml-ld` doesn't read `context.*` files and
            #   fails.
            return

        source = self._apply_redirect(source)

        try:
            ld_rdf = yaml_ld.to_rdf(source)
        except NotFound as not_found:
            logger.info('%s | 404 Not Found', not_found.path)
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(str(namespace)):
                    return self.load(str(namespace))

            logger.info('%s | Cannot find a matching namespace', not_found.path)
            return

        try:
            self.graph.addN(
                parse_quads(
                    quads_document=ld_rdf,
                    graph=source,  # type: ignore
                    blank_node_prefix=str(source),
                ),
            )
            logger.info('%s | loaded successfully.', source)
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

        subject, _predicate, obj = triple

        if isinstance(subject, URIRef):
            self.load(str(subject))

        if isinstance(obj, URIRef):
            self.load(str(obj))

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term

    def _apply_redirect(self, source: str) -> str:
        for pattern, destination in REDIRECTS.items():
            if source.startswith(pattern):
                logger.info('Rewriting: %s → %s', source, destination)
                return destination

        return source
