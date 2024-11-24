import dataclasses
import datetime
import functools
import logging
import time
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Any, Iterable, Mapping

import reasonable
import yaml_ld
from rdflib import (  # noqa: WPS235
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
from rdflib.term import BNode, Node
from requests.exceptions import ConnectionError
from yaml_ld.document_loaders.content_types import ParserNotFound
from yaml_ld.errors import NotFound, YAMLLDError
from yarl import URL

from iolanta.models import Triple, TripleWithVariables
from iolanta.namespaces import IOLANTA
from iolanta.parsers.dict_parser import UnresolvedIRI, parse_quads

logger = logging.getLogger(__name__)

NORMALIZE_TERMS_MAP = MappingProxyType({
    URIRef(_url := 'http://www.w3.org/2002/07/owl'): URIRef(f'{_url}#'),
    URIRef(_url := 'http://www.w3.org/2000/01/rdf-schema'): URIRef(f'{_url}#'),
})


REASONING_ENABLED = True
OWL_REASONING_ENABLED = False


REDIRECTS = MappingProxyType({
    # FIXME This is presently hardcoded; we need to
    #   - either find a way to resolve these URLs automatically,
    #   - or create a repository of those redirects online.
    'http://purl.org/vocab/vann/': 'https://vocab.org/vann/vann-vocab-20100607.rdf',
    str(DC): str(DCTERMS),
    str(RDF): str(RDF),
    str(RDFS): str(RDFS),
    str(OWL): str(OWL),
    str(FOAF): str(FOAF),
})


def construct_flat_triples(algebra: Mapping[str, Any]) -> Iterable[Triple]:
    """Extract flat triples from parsed SPARQL query."""
    if isinstance(algebra, Mapping):
        for key, value in algebra.items():  # noqa: WPS110
            if key == 'triples':
                yield from [   # noqa: WPS353
                    Triple(*raw_triple)
                    for raw_triple in value
                ]

            else:
                yield from construct_flat_triples(value)


def normalize_term(term: Node) -> Node:
    """
    Normalize RDF terms.

    This is an exctremely dirty hack to fix a bug in OWL reported here:

    > https://stackoverflow.com/q/78934864/1245471

    TODO This is:
      * A dirty hack;
      * Based on hard code.
    """
    return NORMALIZE_TERMS_MAP.get(term, term)


@dataclasses.dataclass(frozen=True)
class GlobalSPARQLProcessor(Processor):
    """
    Execute SPARQL queries against the whole Linked Data Web, or The Cyberspace.

    When running the queries, we will try to find and to import pieces of LD
    which can be relevant to the query we are executing.
    """

    graph: ConjunctiveGraph
    inference_lock: Lock = dataclasses.field(default_factory=Lock)

    def __post_init__(self):
        """Note that we do not presently need OWL inference."""
        self.graph.last_not_inferred_source = None

    def query(   # noqa: WPS211, WPS210
        self,
        strOrQuery,
        initBindings=None,
        initNs=None,
        base=None,
        DEBUG=False,
    ):
        """
        Evaluate a query with the given initial bindings, and initial
        namespaces. The given base is used to resolve relative URIs in
        the query and will be overridden by any BASE given in the query.
        """
        initBindings = initBindings or {}
        initNs = initNs or {}

        if isinstance(strOrQuery, Query):
            query = strOrQuery

        else:
            parsetree = parseQuery(strOrQuery)
            query = translateQuery(parsetree, base, initNs)

            triples = construct_flat_triples(query.algebra)
            for triple in triples:
                self.load_data_for_triple(triple, bindings=initBindings)

        self.maybe_apply_inference()
        return evalQuery(self.graph, query, initBindings, base)

    @functools.lru_cache(maxsize=None)    # noqa: B019
    def load(self, source: str):   # noqa: C901, WPS210, WPS212, WPS213, WPS231
        """
        Try to load LD denoted by the given `source`.

        TODO This function is too big, we have to refactor it.
        """
        url = URL(source)

        if url.scheme in {'file', 'python', 'local', 'urn'}:
            # FIXME temporary fix. `yaml-ld` doesn't read `context.*` files and
            #   fails.
            return None

        new_source = self._apply_redirect(source)
        if new_source != source:
            return self.load(new_source)

        if self.graph.get_context(source):
            return None

        # FIXME This is definitely inefficient. However, python-yaml-ld caches
        #   the document, so the performance overhead is not super high.
        try:
            _resolved_source = yaml_ld.load_document(source)['documentUrl']
        except NotFound as not_found:
            logger.info('%s | 404 Not Found', not_found.path)
            namespaces = [RDF, RDFS, OWL, FOAF, DC, VANN]

            for namespace in namespaces:
                if not_found.path.startswith(str(namespace)):
                    self.load(str(namespace))
                    logger.info(
                        'Redirecting %s → namespace %s',
                        not_found.path,
                        namespace,
                    )
                    return None

            logger.info('%s | Cannot find a matching namespace', not_found.path)
            return None

        if _resolved_source:
            _resolved_source_uri_ref = URIRef(_resolved_source)
            if _resolved_source_uri_ref != source:
                self.graph.add((
                    URIRef(source),
                    IOLANTA['redirects-to'],
                    _resolved_source_uri_ref,
                ))
                source = _resolved_source

        self.graph.add((
            URIRef(source),
            RDF.type,
            IOLANTA.Graph,
        ))

        self.graph.add((
            IOLANTA.Graph,
            RDF.type,
            RDFS.Class,
        ))

        try:  # noqa: WPS225
            ld_rdf = yaml_ld.to_rdf(source)
        except ConnectionError as name_resolution_error:
            logger.info(
                '%s | name resolution error: %s',
                source,
                str(name_resolution_error),
            )
            return None
        except ParserNotFound as parser_not_found:
            logger.info('%s | %s', source, str(parser_not_found))
            return None
        except YAMLLDError as yaml_ld_error:
            logger.error('%s | %s', source, str(yaml_ld_error))
            return None

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
            return None

        graph = URIRef(source)
        quad_tuples = [
            tuple([
                normalize_term(term) for term in dataclasses.replace(
                    quad,
                    graph=graph,
                ).as_tuple()
            ])
            for quad in quads
        ]

        self.graph.addN(quad_tuples)
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

        subject, _predicate, rdf_object = triple

        if isinstance(subject, URIRef):
            try:
                self.load(str(subject))
            except Exception:
                logger.exception('Failed to load information about %s', subject)

        if isinstance(rdf_object, URIRef):
            self.load(str(rdf_object))

    def resolve_term(self, term: Node, bindings: dict[str, Node]):
        """Resolve triple elements against initial variable bindings."""
        if isinstance(term, Variable):
            return bindings.get(
                str(term),
                term,
            )

        return term

    def _infer_with_sparql(self):
        """
        Infer triples with SPARQL rules.

        FIXME:
          * Code these rules into SHACL or some other RDF based syntax;
          * Make them available at iolanta.tech/visualizations/ and indexed.
        """
        inference = Path(__file__).parent / 'inference'

        file_names = {
            'wikibase-claim.sparql': URIRef('local:inference-wikibase-claim'),
            'wikibase-statement-property.sparql': URIRef(
                'local:inference-statement-property',
            ),
        }

        for file_name, graph_name in file_names.items():
            start_time = time.time()
            self.graph.update(
                update_object=(inference / file_name).read_text(),
            )
            logger.info(
                '%s: %s triple(s), inferred at %s',
                file_name,
                len(self.graph.get_context(graph_name)),
                datetime.timedelta(seconds=time.time() - start_time),
            )

    def maybe_apply_inference(self):
        """Apply global OWL RL inference if necessary."""
        if not REASONING_ENABLED:
            return

        if self.graph.last_not_inferred_source is None:
            return

        with self.inference_lock:
            self._infer_with_sparql()
            self._infer_with_owl_rl()
            logger.info('Inference @ cyberspace: complete.')

            self.graph.last_not_inferred_source = None

    def _infer_with_owl_rl(self):
        if not OWL_REASONING_ENABLED:
            return

        reasoner = reasonable.PyReasoner()
        reasoner.from_graph(self.graph)
        inferred_triples = reasoner.reason()
        inference_graph_name = BNode('_:inference')
        inferred_quads = [
            (*triple, inference_graph_name)
            for triple in inferred_triples
        ]
        self.graph.addN(inferred_quads)

    def _apply_redirect(self, source: str) -> str:
        for pattern, destination in REDIRECTS.items():
            if source.startswith(pattern):
                logger.info('Rewriting: %s → %s', source, destination)
                return destination

        return source
