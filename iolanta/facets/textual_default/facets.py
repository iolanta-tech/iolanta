import functools
from typing import ClassVar, Iterable
from xml.dom import minidom  # noqa: S408

import funcy
import more_itertools
from rdflib import DC, RDFS, SDO, URIRef
from rdflib.term import BNode, Literal, Node
from rich.syntax import Syntax
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical, VerticalScroll
from textual.events import Click
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static, TabbedContent, TabPane
from textual.worker import Worker, WorkerState
from yarl import URL

from iolanta.cli.formatters.node_to_qname import node_to_qname
from iolanta.facets.errors import FacetNotFound
from iolanta.facets.facet import Facet
from iolanta.models import ComputedQName, NotLiteralNode, Triple


class PropertyName(Widget, can_focus=True, inherit_bindings=False):
    """Property name."""

    DEFAULT_CSS = """
    PropertyName {
        width: 15%;
        height: auto;
        margin-right: 1;
    }
    
    PropertyName:hover {
        background: $boost;
    }
    
    PropertyName:focus {
        background: darkslateblue;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
    ]
    renderable: str | None = reactive[str | None](   # noqa: WPS465
        None,
        init=False,
        layout=True,
    )

    def __init__(
        self,
        iri: NotLiteralNode,
    ):
        """Set the IRI."""
        self.iri = iri
        super().__init__()
        qname = self.app.iolanta.node_as_qname(iri)
        self.renderable = Text(  # noqa: WPS601
            f'⏳ {qname}',
            style='#696969',
        )

    def render_title(self):
        """Render title in a separate thread."""
        output_datatype = URIRef('https://iolanta.tech/env/title')
        return self.app.iolanta.render(self.iri, output_datatype)[0]

    def render(self) -> RenderResult:
        """Render node title."""
        return self.renderable or '…'

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Show the title after it has been rendered."""
        match event.state:
            case WorkerState.SUCCESS:
                self.renderable = event.worker.result   # noqa: WPS601
                self.styles.color = 'white'

            case WorkerState.ERROR:
                raise ValueError(event)

    def action_goto(self):
        """Navigate."""
        self.app.action_goto(self.iri)

    def on_click(self, event: Click):
        """
        Navigate to the property if we are focused.

        TODO: Does not work; causes navigation even if not focused.
        """
        if self.has_focus:
            return self.action_goto()


class Title(Static):
    """Iolanta page title."""

    DEFAULT_CSS = """
    Title {
        padding: 1;
        background: darkslateblue;
        color: white;
        text-style: bold;
    }
    """


class ContentArea(VerticalScroll):
    """Description of the IRI."""

    DEFAULT_CSS = """
    Content {
        layout: vertical;
        height: auto;
        max-height: 100%;
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


class TripleURIRef(URIRef):
    """URN serialization of an RDF triple."""

    @classmethod
    def from_triple(
        cls,
        subject: NotLiteralNode,
        predicate: NotLiteralNode,
        object_: Node,
    ) -> 'TripleURIRef':
        """
        Construct from triple.

        TODO Add special query arguments to conform to RDF standard:
          * subject_bnode
          * predicate_bnode
          * object_bnode
          * object_datatype
          * object_language

        TODO Standardize this?
        """
        iri = URL.build(
            scheme='urn:rdf',
            query={
                'subject': subject,
                'predicate': predicate,
                'object': object_,
            },
        )
        return TripleURIRef(str(iri))

    def as_triple(self) -> Triple:
        """
        Deserialize into a triple.

        TODO support special query arguments described above.
        """
        url = URL(self)
        return Triple(
            subject=URIRef(url.query['subject']),
            predicate=URIRef(url.query['predicate']),
            object=URIRef(url.query['object']),
        )


class PropertyValue(Widget, can_focus=True, inherit_bindings=False):
    """
    Value of a property.

    Supports navigation and provenance.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
        Binding('p', 'provenance', 'Provenan©e'),
    ]

    DEFAULT_CSS = """
    PropertyValue {
        width: auto;
        height: auto;
    }
    
    PropertyValue:hover {
        background: $boost;
    }

    PropertyValue:focus {
        background: darkslateblue;
    }
    """

    renderable: str | None = reactive[str | None](   # noqa: WPS465
        None,
        init=False,
        layout=True,
    )

    def __init__(
        self,
        property_value: Node,
        subject: NotLiteralNode,
        property_iri: NotLiteralNode,
    ):
        """Initialize parameters for rendering, navigation, & provenance."""
        self.property_value = property_value
        self.subject = subject
        self.property_iri = property_iri
        super().__init__()
        qname = self.app.iolanta.node_as_qname(   # noqa: WPS601
            property_value,
        )
        self.renderable = Text(   # noqa: WPS601
            f'⏳ {qname}',
            style='#696969',
        )

    @property
    def iri(self):
        """Return the property IRI for compatibility."""
        return self.property_value

    def render_title(self):
        """Render title in a separate thread."""
        return self.app.iolanta.render(
            self.property_value,
            as_datatype=URIRef('https://iolanta.tech/env/title'),
        )[0]

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Show the title after it has been rendered."""
        match event.state:
            case WorkerState.SUCCESS:
                self.renderable = event.worker.result   # noqa: WPS601
                self.styles.color = 'white'

            case WorkerState.ERROR:
                raise ValueError(event)

    def render(self) -> RenderResult:
        """Render title of the node."""
        return self.renderable

    def action_goto(self):
        """Navigate."""
        self.app.action_goto(self.property_value)

    def action_provenance(self):
        """Navigate to provenance for the property value."""
        self.app.action_goto(
            TripleURIRef.from_triple(
                subject=self.subject,
                predicate=self.property_iri,
                object_=self.property_value,
            ),
        )

    def on_click(self, event: Click):
        """
        Navigate to the property if we are focused.

        FIXME: Does not work; causes navigation even if not focused.
        """
        if self.has_focus:
            return self.action_goto()


class PropertyRow(Widget, can_focus=False, inherit_bindings=False):
    """A container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    PropertyRow {
        width: 1fr;
        height: auto;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """


class PropertiesContainer(Vertical):
    """Contain all properties and their values."""

    DEFAULT_CSS = """
    PropertiesContainer {
        height: auto;
    }"""

    def render_all_properties(self):
        """Render all property names & values."""
        widgets = self.query('PropertyName, PropertyValue')

        widget: PropertyName | PropertyValue
        for widget in widgets:
            widget.renderable = self.app.iolanta.render(
                widget.iri,
                as_datatype=URIRef('https://iolanta.tech/env/title'),
            )[0]

    def on_mount(self):
        """Initiate rendering in the background."""
        self.run_worker(self.render_all_properties, thread=True)


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
            property_name = PropertyName(
                iri=property_iri,
            )

            property_values = [
                PropertyValue(
                    property_value=property_value,
                    subject=self.iri,
                    property_iri=property_iri,
                )
                for property_value in property_values
            ]

            property_values = more_itertools.interleave_longest(
                property_values,
                funcy.repeatedly(
                    functools.partial(
                        Label,
                        ' • ',
                    ),
                    len(property_values) - 1,
                ),
            )

            yield PropertyRow(
                property_name,
                *property_values,
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

        return PropertiesContainer(*self.rows)

    def compose(self) -> Iterable[Widget]:
        """Compose widgets."""
        yield Title(self.title)

        if self.description:
            yield Label(self.description, id='description')

    @property
    def instances(self):
        """Instances of this class."""
        return self.render(
            self.iri,
            as_datatype=URIRef('https://iolanta.tech/cli/default/instances'),
        )

    @property
    def terms(self):
        """Terms of this ontology."""
        return self.render(
            self.iri,
            as_datatype=URIRef('https://iolanta.tech/cli/default/terms'),
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
