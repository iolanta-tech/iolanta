import funcy
from rdflib import Literal
from textual.containers import VerticalScroll

from iolanta.facets.page_title import PageTitle
from iolanta.facets.textual_nanopublication.term_list_widget import TermList
from iolanta.facets.textual_nanopublication.term_widget import TermWidget
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES, DCTERMS, NP
from iolanta.widgets.mixin import IolantaWidgetMixin

NANOPUBLICATION_QUERY = """
SELECT ?assertion ?author ?created_time ?retract WHERE {
    $uri np:hasAssertion ?assertion .

    OPTIONAL {
        $uri (
            dcterms:creator
            | <https://purl.org/pav/createdBy>
            | <https://swan.mindinformatics.org/ontologies/1.2/pav/createdBy>
        ) ?author .
    }

    OPTIONAL {
        $uri dcterms:created ?created_time .
    }

    OPTIONAL {
        GRAPH ?retracting_assertion {
            ?retractor <https://purl.org/nanopub/x/retracts> $uri .
        }

        ?retract np:hasAssertion ?retracting_assertion .
    }
}
"""


class NanopublicationScreen(IolantaWidgetMixin, VerticalScroll):
    """Nanopublication screen."""

    def __init__(self, uri: NotLiteralNode):
        """Initialize."""
        self.uri = uri
        super().__init__()

    def compose(self):
        """Render components of the nanopublication screen."""
        yield PageTitle(NP.Nanopublication)

        row = funcy.first(
            self.iolanta.query(   # noqa: WPS462
                NANOPUBLICATION_QUERY,
                uri=self.uri,
            ),
        )

        if not row:
            return

        yield self.iolanta.render(
            row['assertion'],
            as_datatype=DATATYPES['textual-graph-triples'],
        )

        provenance = []
        if row.get('author'):
            provenance.extend([
                TermWidget(DCTERMS.creator, as_datatype=DATATYPES.icon),
                TermWidget(row['author']),
            ])

        if row.get('created_time'):
            provenance.append(
                TermWidget(row['created_time']),
            )

        if retract := row.get('retract'):
            provenance.extend([
                TermWidget(Literal('Retracted by'), background_color='darkred'),
                TermWidget(retract, background_color='darkred'),
            ])

        if provenance:
            yield TermList(provenance)
