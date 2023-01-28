import logging
from typing import List, Optional, Tuple, Type

from rdflib import ConjunctiveGraph

from iolanta.entry_points import entry_points
from iolanta.graph_providers.base import GraphProvider
from iolanta.graph_providers.errors import GraphCannotBeProvided

logger = logging.getLogger(__name__)


GraphProviderTuple = Tuple[str, Type[GraphProvider]]


def installed_graph_providers() -> List[GraphProviderTuple]:
    """Find installed graph providers."""
    return [
        (entry_point.name, entry_point.load())   # type: ignore
        for entry_point in entry_points(group='iolanta.graph')  # type: ignore
    ]


def construct_graph_from_installed_providers() -> Optional[ConjunctiveGraph]:
    """
    Go over installed providers.

    See if they can provide us with a graph.
    """
    for provider_name, provider_class in installed_graph_providers():
        try:
            return provider_class().retrieve_graph()
        except GraphCannotBeProvided:
            logger.info('Provider %s cannot provide a graph.', provider_name)

    return None
