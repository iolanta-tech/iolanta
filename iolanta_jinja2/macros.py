from typing import Union, Optional, List

from rdflib.term import Node, URIRef

from iolanta.iolanta import Iolanta
from iolanta.renderer import render

Environments = Union[str, List[str]]


def template_render(
    thing: Union[str, Node],
    iolanta: Iolanta,
    environments: Optional[Environments] = None,
):
    """Macro to render something with Iolanta."""
    if ':' not in thing:
        thing = f'local:{thing}'

    thing = iolanta.expand_qname(thing) or thing

    if isinstance(environments, str):
        environments = [environments]

    elif environments is None:
        environments = []

    environments = [
        URIRef(f'local:{environment}') if (
            isinstance(environment, str)
            and ':' not in environment
        ) else environment
        for environment in environments
    ]

    return render(
        node=URIRef(thing),
        iolanta=iolanta,
        environments=[URIRef(environment) for environment in environments],
    )
