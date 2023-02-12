"""
Iolanta facet management.

This module contains a few functions which later will be refactored into
Iolanta - the generic metaverse/cyberspace browser.
"""
import pydoc
from dataclasses import dataclass
from typing import Iterable, List, Optional, Type, Union, cast

from dominate.tags import b, font, table, td, tr
from rdflib.term import Literal, Node, URIRef

from iolanta.facet.base import FacetSearchAttempt
from iolanta.facet.by_environment import FindFacetByEnvironment
from iolanta.facet.by_instance import FindFacetByInstance
from iolanta.facet.by_literal_datatype import FindFacetByLiteralDatatype
from iolanta.facet.by_type import FindFacetByInstanceTypes
from iolanta.facet.errors import FacetNotCallable, FacetNotFound
from iolanta.facet.for_literal import FindFacetForLiteral
from ldflex import LDFlex

HTML = URIRef('https://html.spec.whatwg.org/')


def resolve_facet(iri: URIRef) -> Type['iolanta.Facet']:
    """Resolve a path to a Python object to that object."""
    url = str(iri)

    if not url.startswith('python://'):
        raise Exception(
            'Octadocs only supports facets which are importable Python '
            'callables. The URLs of such facets must start with `python://`, '
            'which {url} does not comply to.'.format(
                url=url,
            ),
        )

    # It is impossible to use `urlpath` for this operation because it (or,
    # rather, one of upper classes from `urllib` that `urlpath` depends upon)
    # will lowercase the URL when parsing it - which means, irreversibly. We
    # have to resort to plain string manipulation.
    import_path = url.replace('python://', '').strip('/')

    facet = cast(Type['iolanta.Facet'], pydoc.locate(import_path))

    if not callable(facet):
        raise FacetNotCallable(
            path=import_path,
            facet=facet,
        )

    return facet


def render_facet(
    node: Node,
    facet: 'iolanta.Facet',
    environments: Optional[List[URIRef]] = None,
    debug_mode: bool = False,
):
    if debug_mode:
        return debug_node(
            node=node,
            environments=environments,
        )

    return facet.show()


def debug_node(node: Union[str, Node], environments: Optional[List[URIRef]]):
    return table(
        tr(
            td(
                b(font('Debug', color='red')),
                colspan=2,
                border=0,
            ),
        ),
        tr(
            td(b(font('Node', color='red')), border=0, align='left'),
            td(str(node), border=0, align='left'),
        ),
        tr(
            td(b(font('Environments', color='red')), border=0, align='left'),
            td(
                ', '.join(
                    map(str, environments),
                ), border=0, align='left',
            ),
        ),
        border=1,
    )


@dataclass
class Render:
    """Facet renderer."""

    ldflex: LDFlex

    def search_for_facet(
        self,
        node: Node,
        environments: List[URIRef],
    ) -> FacetSearchAttempt:
        """Find facet IRI for given node for all environments given."""
        facet_search_attempts = list(
            self.attempt_search_for_facet(
                node=node,
                environments=environments,
            ),
        )

        *failures, success = facet_search_attempts

        if success:
            return success

        raise FacetNotFound(
            node=node,
            environments=environments,
            facet_search_attempts=facet_search_attempts,
        )

    def find_facet_iri(
        self,
        node: Node,
        environments: List[URIRef],
    ) -> URIRef:
        """Find facet IRI for given node for all environments given."""
        return self.search_for_facet(
            node=node,
            environments=environments,
        ).facet

    def attempt_search_for_facet(
        self,
        node: Node,
        environments: List[URIRef],
    ) -> Iterable[FacetSearchAttempt]:
        """
        Stream of attempts to find a facet.

        If this function yields a sequence of N elements, first (N - 1) of those
        are guaranteed to be failures. The remaining one element can be both
        a failure (if nothing was found) or a success (if a facet was found).
        """
        for environment in environments:
            facet_searches = self.find_facet_iri_per_environment(
                node=node,
                environment=environment,
            )

            for facet_search in facet_searches:
                yield facet_search

                if facet_search:
                    return

    def find_facet_iri_per_environment(
        self,
        node: Node,
        environment: URIRef,
    ):
        """Find facet IRI for given node in given env."""
        if isinstance(node, Literal):
            yield from self.find_facet_iri_for_literal(
                literal=node,
                environment=environment,
            )

        yield FindFacetByInstance(
            ldflex=self.ldflex,
            node=node,
            environment=environment,
        )

        yield FindFacetByInstanceTypes(
            ldflex=self.ldflex,
            node=node,
            environment=environment,
        )

        yield FindFacetByEnvironment(
            ldflex=self.ldflex,
            node=node,
            environment=environment,
        )

    def __call__(
        self,
        node: Node,
        environment: URIRef,
    ) -> str:
        ...

    def find_facet_iri_for_literal(self, literal: Literal, environment: URIRef):
        """Find facet IRI for a literal."""
        if literal.datatype is not None:
            yield FindFacetByLiteralDatatype(
                ldflex=self.ldflex,
                node=literal,
                environment=environment,
            )

        yield FindFacetForLiteral(
            ldflex=self.ldflex,
            node=literal,
            environment=environment,
        )

        yield FindFacetByEnvironment(
            ldflex=self.ldflex,
            node=literal,
            environment=environment,
        )
