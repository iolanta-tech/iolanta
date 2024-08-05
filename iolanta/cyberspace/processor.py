import dataclasses
import functools
import logging
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import owlrl
import yaml_ld
from rdflib import (
    DC,
    DCTERMS,
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
from requests.exceptions import ConnectionError
from urllib3.exceptions import NameResolutionError
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import NotFound, YAMLLDError
from yarl import URL

from iolanta.models import Triple, TripleWithVariables
from iolanta.parsers.dict_parser import UnresolvedIRI, parse_quads

logger = logging.getLogger(__name__)


REDIRECTS = {
    # FIXME This is presently hardcoded; we need to
    #   - either find a way to resolve these URLs automatically,
    #   - or create a repository of those redirects online.
    'http://purl.org/vocab/vann/': 'https://vocab.org/vann/vann-vocab-20100607.rdf',
    str(DC): str(DCTERMS),
    str(RDF): str(RDF),
    str(RDFS): str(RDFS),
    str(OWL): str(OWL),
    str(FOAF): str(FOAF),
}


def construct_flat_triples(algebra: Mapping[str, Any]) -> Iterable[Triple]:
    if isinstance(algebra, Mapping):
        for key, value in algebra.items():
            if key == 'triples':
                yield from [Triple(*raw_triple) for raw_triple in value]

            else:
                yield from construct_flat_triples(value)


@dataclass(frozen=True)
class GlobalSPARQLProcessor(Processor):
    graph: ConjunctiveGraph

    def __post_init__(self):
        self.graph.last_not_inferred_source = None

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

        self.maybe_apply_inference()
        return evalQuery(self.graph, query, initBindings, base)

    @functools.lru_cache(maxsize=None)
    def load(self, source: str):
        url = URL(source)

        if url.scheme in {'file', 'python', 'local'}:
            # FIXME temporary fix. `yaml-ld` doesn't read `context.*` files and
            #   fails.
            return

        new_source = self._apply_redirect(source)
        if new_source != source:
            return self.load(new_source)

        if self.graph.get_context(source):
            return

        try:
            ld_rdf = yaml_ld.to_rdf(source)
        except NotFound as not_found:
            logger.info('%s | 404 Not Found', not_found.path)
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(str(namespace)):
                    self.load(str(namespace))
                    logger.info('Redirecting %s → namespace %s', not_found.path, namespace)
                    return

            logger.info('%s | Cannot find a matching namespace', not_found.path)
            return
        except ConnectionError as name_resolution_error:
            logger.info(
                '%s | name resolution error: %s',
                source, str(name_resolution_error),
            )
            return
        except ParserNotFound as parser_not_found:
            logger.info('%s | %s', source, str(parser_not_found))
            return
        except YAMLLDError as yaml_ld_error:
            logger.info('%s | %s', source, str(yaml_ld_error))
            return

        try:
            quads = list(
                parse_quads(
                    quads_document=ld_rdf,
                    graph=source,  # type: ignore
                    blank_node_prefix=str(source),
                ),
            )
        except UnresolvedIRI as err:
            raise dataclasses.replace(
                err,
                context=None,
                iri=source,
            )

        if not quads:
            logger.warning('%s | No data found', source)
            return

        self.graph.addN(quads)
        self.graph.last_not_inferred_source = source
        logger.info('%s | loaded successfully.', source)

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

    def maybe_apply_inference(self):
        if self.graph.last_not_inferred_source is None:
            return

        closure_class = owlrl.OWLRL_Extension
        logger.info(
            'Inference @ cyberspace: %s (due to %s) started…',
            closure_class.__name__,
            self.graph.last_not_inferred_source,
        )
        owlrl.DeductiveClosure(closure_class).expand(self.graph)
        logger.info('Inference @ cyberspace: complete.')

        self.graph.last_not_inferred_source = None
