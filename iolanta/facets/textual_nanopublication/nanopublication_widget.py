import funcy
from textual.containers import VerticalScroll

from iolanta.facets.page_title import PageTitle
from iolanta.facets.textual_nanopublication.term_list_widget import TermList
from iolanta.facets.textual_nanopublication.term_widget import TermWidget
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES, DCTERMS, NP
from iolanta.widgets.mixin import IolantaWidgetMixin


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
                """
                SELECT ?assertion ?author ?created_time WHERE {
                    $uri
                        np:hasAssertion ?assertion ;
                        (
                            dcterms:creator
                            | <https://purl.org/pav/createdBy>
                        ) ?author ;
                        dcterms:created ?created_time .
                }
                """,
                uri=self.uri,
            ),
        )

        if not row:
            return

        rows = self.iolanta.query(   # noqa: WPS462
            """
            SELECT ?subject ?predicate ?object WHERE {
                GRAPH $graph {
                    ?subject ?predicate ?object .
                }
            }
            ORDER BY ?subject ?predicate ?object
            """,
            graph=row['assertion'],
        )

        yield TermList([
            TermWidget(term)
            for row in rows
            for term in row.values()
        ] + [
            TermWidget(DCTERMS.creator, as_datatype=DATATYPES.icon),
            TermWidget(row['author']),
            TermWidget(row['created_time']),
        ])
