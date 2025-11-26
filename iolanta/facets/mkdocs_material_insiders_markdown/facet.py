from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rdflib import URIRef

from iolanta.facets.facet import Facet
from iolanta.namespaces import DATATYPES, IOLANTA, RDF, RDFS


class MkDocsMaterialInsidersMarkdownFacet(Facet[str]):
    """Render rdfs:Datatype nodes as mkdocs-material-insiders-markdown."""
    
    META = Path(__file__).parent / 'data' / 'mkdocs_material_insiders_markdown.yamlld'
    """Render rdfs:Datatype nodes as mkdocs-material-insiders-markdown."""

    @property
    def _template_env(self) -> Environment:
        """Jinja2 template environment."""
        template_path = Path(__file__).parent / 'templates'
        return Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=False,
        )

    def show(self) -> str:
        """Render the datatype as markdown."""
        # Get the label using title facet
        label = self.render(
            self.this,
            as_datatype=DATATYPES.title,
        )

        # Get the comment/description
        comment_rows = self.query(
            """
            SELECT ?comment WHERE {
                $this rdfs:comment ?comment .
            }
            LIMIT 1
            """,
            this=self.this,
        )
        comment = str(comment_rows[0]['comment']) if comment_rows else None

        # Get all types (rdf:type)
        type_rows = self.query(
            """
            SELECT ?type WHERE {
                $this rdf:type ?type .
            }
            """,
            this=self.this,
        )
        types = [
            {
                'uri': row['type'],
                'title': self.render(row['type'], as_datatype=DATATYPES.title),
            }
            for row in type_rows
        ]

        # Get all superclasses (rdfs:subClassOf)
        superclass_rows = self.query(
            """
            SELECT ?superclass WHERE {
                $this rdfs:subClassOf ?superclass .
            }
            """,
            this=self.this,
        )
        superclasses = [
            {
                'uri': row['superclass'],
                'title': self.render(row['superclass'], as_datatype=DATATYPES.title),
            }
            for row in superclass_rows
        ]

        template = self._template_env.get_template('datatype.jinja2.md')
        return template.render(
            label=label,
            comment=comment,
            types=types,
            superclasses=superclasses,
        )

