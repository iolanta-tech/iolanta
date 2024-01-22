from rdflib import Literal, URIRef

from iolanta.iolanta import Iolanta


def test_render_label():
    Iolanta().render(
        Literal('type'),
        environments=[URIRef('https://iolanta.tech/cli/link')],
    )
