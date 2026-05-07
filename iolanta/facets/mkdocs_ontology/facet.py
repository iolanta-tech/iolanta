from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rdflib.term import Node

from iolanta.facets.facet import Facet
from iolanta.namespaces import DATATYPES


class TermStatus(StrEnum):
    """Status of an ontology term."""

    STABLE = "stable"
    ARCHAIC = "archaic"
    TESTING = "testing"
    UNSTABLE = "unstable"


@dataclass(frozen=True)
class _Term:
    """Term IRI plus its rendered title and optional comment."""

    uri: str
    title: str
    comment: str | None


class MkDocsOntologyFacet(Facet[str]):
    """Render an `owl:Ontology` as Material for MkDocs Markdown."""

    META = Path(__file__).parent / 'data' / 'mkdocs_ontology.yamlld'  # noqa: WPS115

    def show(self) -> str:
        """Render the ontology as Markdown."""
        groups = list(self._build_groups())
        template = self._template_env.get_template('ontology.jinja2.md')
        return template.render(groups=groups)

    @property
    def _template_env(self) -> Environment:
        """Jinja2 template environment."""
        template_path = Path(__file__).parent / 'templates'
        return Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,
        )

    @cached_property
    def _term_rows(self) -> list[dict[str, object]]:
        return self.stored_query("terms.sparql", iri=self.this)

    def _build_groups(self) -> list[dict[str, object]]:
        ordered_titles: list[str | None] = []
        groups_by_title: dict[str | None, dict[str, _Term]] = {}

        for row in self._term_rows:
            status = self._row_status(row)
            if status == TermStatus.ARCHAIC:
                continue

            term = self._term_from_row(row)
            title = self._group_title_for_row(row)

            existing = groups_by_title.get(title)
            if existing is None:
                ordered_titles.append(title)
                groups_by_title[title] = {term.uri: term}
            else:
                existing.setdefault(term.uri, term)

        return [
            {"title": title, "terms": list(groups_by_title[title].values())}
            for title in ordered_titles
        ]

    def _row_status(self, row: dict[str, object]) -> TermStatus:
        status_literal = row.get("status")
        status_value = (
            status_literal.value
            if status_literal is not None and hasattr(status_literal, "value")
            else "stable"
        )
        return TermStatus(status_value)

    def _term_from_row(self, row: dict[str, object]) -> _Term:
        term_node = self._row_node(row, "term")
        comment_literal = row.get("comment")
        return _Term(
            uri=str(term_node),
            title=str(self.render(term_node, as_datatype=DATATYPES.title)),
            comment=str(comment_literal) if comment_literal is not None else None,
        )

    def _group_title_for_row(self, row: dict[str, object]) -> str | None:
        group = row.get("group")
        if not isinstance(group, Node):
            return None
        return str(self.render(group, as_datatype=DATATYPES.title))

    def _row_node(self, row: dict[str, object], key: str) -> Node:
        candidate = row[key]
        if not isinstance(candidate, Node):
            raise TypeError(f"Expected RDF Node for `{key}`, got {type(candidate)}")
        return candidate
