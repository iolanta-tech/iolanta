from typing import ClassVar

from rdflib import Literal, URIRef
from rdflib.term import Node
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical, VerticalScroll
from textual.events import Click
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, TabbedContent, TabPane
from textual.worker import Worker, WorkerState

from iolanta.facets.textual_default.triple_uri_ref import TripleURIRef
from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES


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
    renderable: str | None = reactive[str | None](  # noqa: WPS465
        None,
        init=False,
        layout=True,
    )

    def __init__(
        self,
        iri: NotLiteralNode,
        qname: str,
    ):
        """Set the IRI."""
        self.iri = iri
        super().__init__()
        self.renderable = Text(  # noqa: WPS601
            f'⏳ {qname}',
            style='#696969',
        )

    def render_title(self):
        """Render title in a separate thread."""
        return self.app.iolanta.render(self.iri, DATATYPES.title)

    def render(self) -> RenderResult:
        """Render node title."""
        return self.renderable or '…'

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Show the title after it has been rendered."""
        match event.state:
            case WorkerState.SUCCESS:
                self.renderable = event.worker.result  # noqa: WPS601
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
        padding-right: 1;
        padding-bottom: 1;
    }

    PropertyValue:hover {
        background: $boost;
    }

    PropertyValue:focus {
        background: darkslateblue;
    }
    """

    renderable: str | None = reactive[str | None](  # noqa: WPS465
        None,
        init=False,
        layout=True,
    )

    def __init__(
        self,
        property_value: Node,
        subject: NotLiteralNode,
        property_iri: NotLiteralNode,
        property_qname: str,
    ):
        """Initialize parameters for rendering, navigation, & provenance."""
        self.property_value = property_value
        self.subject = subject
        self.property_iri = property_iri
        super().__init__()
        self.renderable = Text(  # noqa: WPS601
            f'⏳ {property_qname}',
            style='#696969',
        )

    @property
    def iri(self):
        """Return the property IRI for compatibility."""
        return self.property_value

    def on_worker_state_changed(self, event: Worker.StateChanged):
        """Show the title after it has been rendered."""
        match event.state:
            case WorkerState.SUCCESS:
                self.renderable = event.worker.result  # noqa: WPS601
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
                as_datatype=DATATYPES.title,
            )

    def on_mount(self):
        """Initiate rendering in the background."""
        self.run_worker(self.render_all_properties, thread=True)


class PropertyValues(Widget):
    """Container for property values."""

    MAX_COLUMN_COUNT = 6

    DEFAULT_CSS = """
    PropertyValues {
        layout: grid;
        grid-size: 6;
        height: auto;
        max-width: 85%;
    }
    """

    def on_mount(self):
        """Adjust column count based on children of this node."""
        children_count = len(self.children)
        self.styles.grid_size_columns = max(
            min(
                children_count,
                self.MAX_COLUMN_COUNT,
            ),
            1,
        )


class PropertyRow(Widget, can_focus=False, inherit_bindings=False):
    """A container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    PropertyRow {
        width: 1fr;
        height: auto;
        layout: horizontal;
    }
    """


class LiteralPropertyValue(Widget, can_focus=True, inherit_bindings=False):
    """
    Literal value of a property.

    Supports provenance.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('p', 'provenance', 'Provenan©e'),
    ]

    DEFAULT_CSS = """
    LiteralPropertyValue {
        width: auto;
        height: auto;
    }

    LiteralPropertyValue:hover {
        background: $boost;
    }

    LiteralPropertyValue:focus {
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
        property_value: Literal,
        subject: NotLiteralNode,
        property_iri: NotLiteralNode,
    ):
        """Initialize parameters for rendering, navigation, & provenance."""
        self.property_value = property_value
        self.subject = subject
        self.property_iri = property_iri
        super().__init__()
        self.renderable = Text(   # noqa: WPS601
            str(property_value),
            style='#696969',
        )

    @property
    def iri(self):
        """Return the property IRI for compatibility."""
        return self.property_value

    def render(self) -> RenderResult:
        """Render title of the node."""
        return self.renderable

    def action_provenance(self):
        """Navigate to provenance for the property value."""
        self.app.action_goto(
            TripleURIRef.from_triple(
                subject=self.subject,
                predicate=self.property_iri,
                object_=self.property_value,
            ),
        )


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
