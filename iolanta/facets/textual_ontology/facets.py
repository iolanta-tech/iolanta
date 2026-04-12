from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property

import funcy
from rdflib import URIRef
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.facets.textual_ontology.widgets import (
    TermCardRowStack,
    TermGroupSection,
    TermsContent,
)
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES


class TermStatus(StrEnum):
    """Status of an ontology term."""

    STABLE = "stable"
    ARCHAIC = "archaic"
    TESTING = "testing"
    UNSTABLE = "unstable"


@dataclass
class TermAndStatus:
    term: URIRef
    status: TermStatus


class OntologyFacet(Facet[Widget]):
    """Render an ontology."""

    @cached_property
    def grouped_terms(
        self,
    ) -> dict[NotLiteralNode | None, list[TermAndStatus]]:
        """Group terms by VANN categories."""
        rows = self.stored_query("terms.sparql", iri=self.this)
        grouped = [
            (
                row.get("group"),
                TermAndStatus(
                    term=row["term"],
                    status=status,
                ),
            )
            for row in rows
            if (
                status := TermStatus(
                    (status_literal := row.get("status"))
                    and status_literal.value
                    or "stable",
                )
            )
            != TermStatus.ARCHAIC
        ]

        return funcy.group_values(grouped)

    def show(self) -> Widget:
        """Render widget."""
        self._log_index_and_vocabs()

        return Vertical(
            PageTitle(self.this),
            TermsContent(
                *(
                    self._group_section(group, rows)
                    for group, rows in self.grouped_terms.items()
                ),
            ),
        )

    def _log_index_and_vocabs(self) -> None:
        index_title = self.render(
            "https://iolanta.tech/visualizations/index.yaml",
            as_datatype=DATATYPES.title,
        )
        self.logger.info("Index Retrieved: %s", index_title)

        vocabs = funcy.lpluck(
            "vocab",
            self.stored_query("visualization-vocab.sparql", iri=self.this),
        )

        for vocab in vocabs:
            vocab_title = self.render(
                vocab,
                as_datatype=DATATYPES.title,
            )
            self.logger.info(
                "Visualization vocabulary retrieved: %s",
                vocab_title,
            )

    def _group_section(
        self,
        group: NotLiteralNode | None,
        rows: list[TermAndStatus],
    ) -> TermGroupSection:
        stack = TermCardRowStack(*(row.term for row in rows))
        if group is None:
            return TermGroupSection(stack)

        group_title = self.render(group, as_datatype=DATATYPES.title)
        return TermGroupSection(
            Static(f"[b]{group_title}[/b]"),
            stack,
        )
