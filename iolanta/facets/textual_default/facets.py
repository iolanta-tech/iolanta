import functools
from typing import Iterable
from xml.dom import minidom  # noqa: S408

import funcy
import more_itertools
from rdflib import DC, RDFS, SDO, URIRef
from rdflib.term import BNode, Literal, Node
from rich.syntax import Syntax
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, Static, TabbedContent, TabPane

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.errors import FacetNotFound
from iolanta.facets.facet import Facet
from iolanta.models import ComputedQName, NotLiteralNode


class PropertyName(Static):
    """Property name."""

    DEFAULT_CSS = """
    PropertyName {
        width: 15%;
        padding-right: 1;
    }
    """

    def render(self) -> RenderResult:
        environment = URIRef('https://iolanta.tech/env/title' if self.app.is_provenance_mode else 'https://iolanta.tech/cli/link')
        return self.iolanta.render(self.iri, [environment])[0]


class ContentArea(VerticalScroll):
    """Description of the IRI."""

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

    def compose(self) -> ComposeResult:
        """Render tabs."""
        with TabbedContent():
            for label, tab_content in self.tabs.items():
                if tab_content is None:
                    raise ValueError(
                        f'Tab `{label}` is `None` and is not renderable.',
                    )

                with TabPane(label):
                    yield tab_content


class TextualDefaultFacet(Facet[Widget]):   # noqa: WPS214
    """Default rendering engine."""

    @functools.cached_property
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

    @functools.cached_property
    def rows(self):
        """Generate rows for the properties table."""
        for property_iri, property_values in self.grouped_properties.items():
            property_name = PropertyName()
            property_name.iri = property_iri
            property_name.iolanta = self.iolanta

            property_values = [
                Label(
                    self.render(
                        property_value,
                        environments=[URIRef('https://iolanta.tech/cli/link')],
                    ),
                )
                for property_value in property_values
            ]

            separators = list(
                funcy.repeatedly(
                    functools.partial(Label, ' · '),
                    len(property_values) - 1,
                ),
            )

            property_values_with_separators = more_itertools.interleave_longest(
                property_values,
                separators,
            )

            yield Horizontal(
                property_name,
                *property_values_with_separators,
            )

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
                f"[@click=app.goto('{qname.namespace_url}')]{qname.namespace_name}[/]"
            )
            term_part = qname.term if iri == self.iri else (
                f"[@click=app.goto('{iri}')]{qname.term}[/]"
            )

            return f'{namespace_part}:{term_part}'

        if iri == self.iri:
            return str(iri)

        return f"[@click=app.goto('{iri}')]{iri}[/]"

    @functools.cached_property
    def description(self) -> str | Syntax | None:
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

        return Vertical(*self.rows)

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

    @property
    def instances(self):
        """Instances of this class."""
        return self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/cli/default/instances')],
        )

    @property
    def terms(self):
        """Terms of this ontology."""
        return self.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/cli/default/terms')],
        )

    @property
    @funcy.post_processing(dict)
    def tabs(self):
        """
        Tabs available for this IRI.

        TODO: Make this dynamic with `.render_all()`.
        """
        try:
            yield 'Instances', self.instances
        except FacetNotFound:
            ...   # noqa: WPS428

        try:
            yield 'Terms', self.terms
        except FacetNotFound:
            ...   # noqa: WPS428

        yield 'Properties', self.properties

    def show(self) -> Widget:
        """Render the content."""
        area = ContentArea(*self.compose())
        area.tabs = self.tabs
        return area
