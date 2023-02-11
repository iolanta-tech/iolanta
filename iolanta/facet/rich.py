from abc import ABC
from typing import Any, Protocol, Union

from iolanta.facet import Facet


class Rich(Protocol):
    __rich__: Any  # type: ignore


Renderable = Union[Rich, str]


class RichFacet(ABC, Facet[Renderable]):
    """Render stuff in console with Rich."""
