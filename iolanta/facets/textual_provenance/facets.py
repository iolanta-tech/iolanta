from typing import ClassVar

import funcy
from rdflib import URIRef
from rdflib.term import BNode, Literal, Node
from textual.app import ComposeResult, RenderResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from iolanta.facets.facet import Facet
from iolanta.facets.textual_default.facets import PropertyName
from iolanta.facets.textual_default.triple_uri_ref import TripleURIRef
from iolanta.facets.textual_default.widgets import PropertyRow, Title
from iolanta.models import NotLiteralNode, Triple
from iolanta.namespaces import LOCAL, RDF


class RDFTermView(Widget, can_focus=True, inherit_bindings=False):
    """Display and navigate to an RDF term."""

    DEFAULT_CSS = """
    RDFTermView {
        width: auto;
        height: auto;
    }

    RDFTermView:hover {
        background: $boost;
    }

    RDFTermView:focus {
        background: darkslateblue;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
    ]

    def __init__(self, node: Node):
        """Initialize."""
        self.node = node
        super().__init__()

    def action_goto(self):
        """Navigate."""
        self.app.action_goto(self.node)

    def render(self) -> RenderResult:
        """Render the RDF term."""
        icon = {
            URIRef: '🔗',  # Represents a link or URL
            BNode: '⬜️',  # Represents a blank or undefined node
            Literal: '🔤',  # Represents text or a literal value
        }[type(self.node)]
        return f'{icon} {self.node}'


class ProvenanceView(Vertical):
    """Triple provenance page."""

    def __init__(
        self,
        triple: Triple,
        graphs: list[NotLiteralNode],
    ):
        """Initialize."""
        self.triple = triple
        self.graphs = graphs
        super().__init__()

    @property
    def graph_views(self):
        """Construct widgets to render the graph references."""
        return [RDFTermView(graph) for graph in self.graphs]

    def compose(self) -> ComposeResult:
        """Build page structure."""
        yield Title('Provenan©e for a triple')

        # TODO: Calculate QNames somehow.
        yield PropertyRow(
            PropertyName(RDF.subject, qname=str(RDF.subject)),
            RDFTermView(self.triple.subject),
        )

        yield PropertyRow(
            PropertyName(RDF.predicate, qname=str(RDF.predicate)),
            RDFTermView(self.triple.predicate),
        )

        yield PropertyRow(
            PropertyName(RDF.object, qname=str(RDF.object)),
            RDFTermView(self.triple.object),
        )

        yield Label('[b]Appearances[/b]')

        if self.graphs:
            yield from self.graph_views
        else:
            yield Label('None detected ☹')


class TextualProvenanceFacet(Facet[Widget]):
    """Facet for a triple."""

    def show(self) -> Widget:
        """Obtain & render provenance info."""
        uri = TripleURIRef(self.iri)
        triple = uri.as_triple()

        graphs = funcy.lpluck(
            'graph',
            self.stored_query(
                'graphs.sparql',
                subject=triple.subject,
                predicate=triple.predicate,
                object=triple.object,
            ),
        )

        if not graphs:
            exists = self.stored_query(
                'triples.sparql',
                subject=triple.subject,
                predicate=triple.predicate,
                object=triple.object,
            )

            if exists:
                graphs = [LOCAL.term('_inference')]

        return ProvenanceView(
            triple=triple,
            graphs=graphs,
        )
