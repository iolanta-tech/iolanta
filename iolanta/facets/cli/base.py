from abc import ABC
from typing import Any, Protocol, Union

from rich.text import Text

from iolanta.facets.facet import Facet


class Rich(Protocol):
    __rich__: Any  # type: ignore


Renderable = str | Rich | Text


class RichFacet(ABC, Facet[Renderable]):
    """Render stuff in console with Rich."""
