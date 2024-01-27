import logging
import sys
import traceback
from functools import cached_property
from pathlib import Path
from typing import Iterable

import funcy
import rdflib
from rdflib import URIRef, DC, SDO, RDFS
from rdflib.term import Node, Literal, BNode
from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static, DataTable

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.facet import Facet
from iolanta.models import ComputedQName, NotLiteralNode
from iolanta.namespaces import IOLANTA


class Content(VerticalScroll):
    DEFAULT_CSS = """
    Content {
        layout: vertical;
        overflow-x: hidden;
        overflow-y: auto;
    }
    
    #title {
        padding: 1;
        background: darkslateblue;
    }
    
    #description {
        padding: 1;
    }
        
    #properties {
        padding: 1;
    }
    
    /* FIXME: This one does not work */
    DataTable .datatable--header {
        background: purple;
        color: red;
    }
    """


class TextualDefaultFacet(Facet[Widget]):
    """Default rendering engine."""

    @cached_property
    def grouped_properties(self) -> dict[NotLiteralNode, list[Node]]:
        """Properties of current node & their values."""
        property_rows = self.stored_query(
            'properties.sparql',
            iri=self.iri,
        )

        property_pairs = [
            (row['property'], row['object'])
            for row in property_rows
        ]

        return funcy.group_values(property_pairs)

    @property
    def title(self) -> str:
        """
        Candidates for the page title.

        FIXME: Here, we mutate `grouped_properties` :(

        TODO: Implement locale support.
        """
        choices = [
            title
            for title_property in [DC.title, SDO.title, RDFS.label]
            for title in self.grouped_properties.pop(title_property, [])
            if isinstance(title, Literal)
        ]

        if choices:
            return choices[0].value

        return self.format_clickable_link(self.iri)

    def format_clickable_link(self, iri: NotLiteralNode):
        """Format given IRI as clickable link, if possible."""
        if isinstance(iri, BNode):
            return str(iri)

        qname: ComputedQName | NotLiteralNode = node_to_qname(
            iri,
            self.iolanta.graph,
        )
        if isinstance(qname, ComputedQName):
            namespace_part = (
                f"[@click=goto('{qname.namespace_url}')]{qname.namespace_name}[/]"
            )
            term_part = qname.term if iri == self.iri else (
                f"[@click=goto('{iri}')]{qname.term}[/]"
            )

            return f'{namespace_part}:{term_part}'

        if iri == self.iri:
            return str(iri)

        return f"[@click=goto('{iri}')]{iri}[/]"

    @cached_property
    def description(self) -> str | None:
        """
        Candidates for description.

        FIXME: We mutate `grouped_properties` here.
        """
        choices = [
            description
            for description_property in [
                DC.description,
                SDO.description,
                RDFS.comment,
            ]
            for description in self.grouped_properties.pop(description_property, [])
            if isinstance(description, Literal)
        ]

        try:
            return choices[0].value
        except IndexError:
            return None

    @cached_property
    def properties(self) -> Widget | None:
        if not self.grouped_properties:
            return None

        properties_table = DataTable(show_header=True, show_cursor=False)
        properties_table.add_columns('Property', 'Value')
        properties_table.add_rows([
            (
                self.render(
                    property_iri,
                    environments=[URIRef('https://iolanta.tech/cli/link')]
                ),
                ' · '.join(
                    self.render(
                        property_value,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    )
                    for property_value in property_values
                ),
            )
            for property_iri, property_values in self.grouped_properties.items()
        ])

        return properties_table

    def compose(self) -> Iterable[Widget]:
        """Compose widgets."""
        yield Static(
            f'[bold white]{self.title}[/bold white]',
            id='title',
        )

        if self.description:
            yield Label(self.description, id='description')

        sub_facets = list(
            self.render_all(
                self.iri,
                environment=URIRef('https://iolanta.tech/cli/default'),
            ),
        )

        if sub_facets:
            yield from sub_facets

        elif self.properties:
            yield Label('[i]Properties[/i]', id='properties')
            yield self.properties


    def show(self) -> Widget:
        return Content(*self.compose())



        nodes_for_property = [
            (row['subject'], row['object'])
            for row in self.stored_query(
                'nodes-for-property.sparql',
                iri=self.iri,
            )
        ]
        if nodes_for_property:
            rendered_property = self.render(
                self.iri,
                environments=[URIRef('https://iolanta.tech/cli/link')],
            )

            children.append(Label(
                '\n[bold]A few nodes connected with this property[/]\n'
            ))
            nodes_table = DataTable(show_header=False, show_cursor=False)
            nodes_table.add_columns('Subject', 'Property', 'Object')
            nodes_table.add_rows([(
                    self.render(
                        subject_node,
                        environments=[URIRef('https://iolanta.tech/cli/link')],
                    ),
                    rendered_property,
                    self.render(
                        object_node,
                        environments=[URIRef('https://iolanta.tech/cli/link')]
                    ))
                for subject_node, object_node in nodes_for_property
            ])

            children.append(nodes_table)

        if self.grouped_properties:


            children.append(Label('\n[bold]Properties[/]\n'))

        return Vertical(*children)
