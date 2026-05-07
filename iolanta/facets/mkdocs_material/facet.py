from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader

from iolanta.facets.facet import Facet
from iolanta.namespaces import DATATYPES
from iolanta.query_result import SelectResult


class MkDocsMaterialFacet(Facet[str]):
    """Render rdfs:Datatype nodes as mkdocs-material markdown."""

    META = Path(__file__).parent / "data" / "mkdocs_material.yamlld"  # noqa: WPS115

    def show(self) -> str:
        """Render the datatype as markdown."""
        template = self._template_env.get_template("datatype.jinja2.md")
        return template.render(
            label=self.render(self.this, as_datatype=DATATYPES.title),
            comment=self._first_comment(),
            types=self._related_terms("rdf:type ?related"),
            superclasses=self._related_terms("rdfs:subClassOf ?related"),
        )

    @property
    def _template_env(self) -> Environment:
        """Jinja2 template environment."""
        template_path = Path(__file__).parent / "templates"
        return Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,
        )

    def _first_comment(self) -> str | None:
        rows = cast(
            SelectResult,
            self.query(
                """
                SELECT ?comment WHERE {
                    $this rdfs:comment ?comment .
                }
                LIMIT 1
                """,
                this=self.this,
            ),
        )
        return str(rows[0]["comment"]) if rows else None

    def _related_terms(self, pattern: str) -> list[dict[str, object]]:
        rows = cast(
            SelectResult,
            self.query(
                f"""
                SELECT ?related WHERE {{
                    $this {pattern} .
                }}
                """,
                this=self.this,
            ),
        )
        return [
            {
                "uri": row["related"],
                "title": self.render(row["related"], as_datatype=DATATYPES.title),
            }
            for row in rows
        ]
