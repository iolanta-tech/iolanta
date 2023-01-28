from abc import ABC

from dominate.tags import html_tag

from iolanta.facet import Facet


class HTMLFacet(ABC, Facet[html_tag]):
    """Render as HTML."""
