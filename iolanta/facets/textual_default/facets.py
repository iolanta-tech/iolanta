import functools
from xml.dom import minidom  # noqa: S408

import funcy
from rdflib.term import Literal, Node
from rich.syntax import Syntax
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from iolanta.facets.facet import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.facets.textual_default.widgets import (
    LiteralPropertyValue,
    PropertiesContainer,
    PropertyName,
    PropertyRow,
    PropertyValue,
    PropertyValues,
)
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DC, RDFS, SDO


class Description(Static):
    """Static widget with padding for descriptions."""

    DEFAULT_CSS = """
    Description {
        padding: 1;
    }
    """


class TextualDefaultFacet(Facet[Widget]):   # noqa: WPS214
    """Default rendering engine."""

    query_file_name = 'properties.sparql'
    properties_on_the_right = False

    @functools.cached_property
    def grouped_properties(self) -> dict[NotLiteralNode, list[Node]]:
        """Properties of current node & their values."""
        property_rows = self.stored_query(
            self.query_file_name,
            this=self.this,
        )

        property_pairs = [
            (row['property'], row['object'])
            for row in property_rows
        ]

        property_pairs = [
            (property_iri, object_node)
            for property_iri, object_node in property_pairs
            if (
                not isinstance(object_node, Literal)
                or not (language := object_node.language)  # noqa: W503
                or (language == self.iolanta.language)     # noqa: W503
            )
        ]

        return funcy.group_values(property_pairs)

    @functools.cached_property
    def rows(self):
        """Generate rows for the properties table."""
        for property_iri, property_values in self.grouped_properties.items():
            property_name = PropertyName(
                iri=property_iri,
                qname=self.iolanta.node_as_qname(property_iri),
            )

            property_values = [
                LiteralPropertyValue(
                    property_value=property_value,
                    subject=self.this,
                    property_iri=property_iri,
                ) if isinstance(property_value, Literal) else PropertyValue(
                    property_value=property_value,
                    subject=self.this,
                    property_iri=property_iri,
                    property_qname=self.iolanta.node_as_qname(property_iri),
                )
                for property_value in property_values
            ]

            if self.properties_on_the_right:
                # Property name on the right (last column), values on the left (first column)
                yield PropertyRow(
                    PropertyValues(*property_values),
                    property_name,
                )
            else:
                # Property name on the left (first column), values on the right (last column)
                yield PropertyRow(
                    property_name,
                    PropertyValues(*property_values),
                )

    @functools.cached_property
    def description(self) -> str | Syntax | None:
        """
        Candidates for description.

        FIXME: We mutate `grouped_properties` here.

        TODO: Move into a separate Facet.
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
            literal = choices[0]
        except IndexError:
            return None

        literal_value = literal.value

        match literal_value:
            case str() as string:
                return string

            case minidom.Document() as xml_document:
                return Syntax(
                    xml_document.toxml(),
                    'xml',
                )

            case something_else:
                type_of_something_else = type(something_else)
                raise ValueError(
                    f'What is this? {something_else} '   # noqa: WPS326
                    f'is a {type_of_something_else}!',   # noqa: WPS326
                )

    @functools.cached_property
    def properties(self) -> Widget | None:
        """Render properties table."""
        if not self.grouped_properties:
            return Static('No properties found ☹')

        return PropertiesContainer(*self.rows)

    def show(self) -> Widget:
        """Render the content."""

        widgets = [PageTitle(self.this)]

        if self.description:
            widgets.append(Description(self.description))
        
        widgets.append(self.properties)

        return VerticalScroll(*widgets)


class PageFooter(PageTitle):
    """Page footer."""

    DEFAULT_CSS = """
    PageFooter {
        dock: bottom;
        background: darkmagenta;
    }
    """

class InverseProperties(TextualDefaultFacet):
    """Inverse properties view."""

    query_file_name = 'inverse-properties.sparql'
    properties_on_the_right = True

    def show(self) -> Widget:
        """Render the content."""
        return Vertical(
            VerticalScroll(
                self.properties,
            ),
            PageFooter(self.this, extra='[i]& its inverse RDF properties[/i]'),
        )
