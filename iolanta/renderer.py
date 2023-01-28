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
from iolanta.facet.errors import FacetNotCallable, FacetNotFound, FacetError
from iolanta.facet.facet import Facet
from iolanta.facet.for_literal import FindFacetForLiteral
from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode
from ldflex import LDFlex

HTML = URIRef('https://html.spec.whatwg.org/')


def resolve_facet(iri: URIRef) -> Type[Facet]:
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

    facet = cast(Type[Facet], pydoc.locate(import_path))

    if not callable(facet):
        raise FacetNotCallable(
            path=import_path,
            facet=facet,
        )

    if not issubclass(facet, Facet):
        raise ValueError(f'{facet} is not a Facet.')

    return facet


def _render_facet(
    node: Node,
    facet: Facet,
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


def render(
    node: Union[str, Node],
    iolanta: Iolanta,
    environments: Optional[Union[str, List[NotLiteralNode]]] = None,
) -> str:
    """Find an Iolanta facet for a node and render it."""
    if isinstance(environments, str):
        environments = [environments]

    if not environments:
        environments = [HTML]

    iolanta.logger.debug('Environments: %s', environments)

    facet_search_attempt = Render(
        ldflex=iolanta.ldflex,
    ).search_for_facet(
        node=node,
        environments=environments,
    )

    facet_class = resolve_facet(
        iri=facet_search_attempt.facet,
    )

    facet = facet_class(
        iri=node,
        iolanta=iolanta,
        environment=facet_search_attempt.environment,
    )

    try:
        return _render_facet(
            node=node,
            facet=facet,
            environments=environments,
            debug_mode=False,    # iolanta.is_debug_mode(node),
        )

    except (FacetError, FacetNotFound):   # noqa: WPS329
        # Prevent nested `FacetError` exceptions.
        raise

    except Exception as err:
        raise FacetError(
            node=node,
            facet_iri=facet_search_attempt.facet,
            facet_search_attempt=facet_search_attempt,
            error=err,
        ) from err


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
