from typing import ClassVar

from rdflib.term import Node
from rich.text import Text
from textual.app import RenderResult
from textual.binding import Binding, BindingType
from textual.events import Click
from textual.reactive import reactive
from textual.widget import Widget
from textual.worker import Worker, WorkerState

from iolanta.facets.textual_default.triple_uri_ref import TripleURIRef
from iolanta.facets.textual_nanopublication.models import TermPositionInTriple
from iolanta.models import NotLiteralNode, Triple
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin


class TermWidget(   # noqa: WPS214
    IolantaWidgetMixin,
    Widget,
    can_focus=True,
    inherit_bindings=False,
):
    """Widget to display a term."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('enter', 'goto', 'Goto'),
    ]

    DEFAULT_CSS = """
    TermWidget {
        width: auto;
        height: auto;
        padding: 1 2;
    }

    TermWidget:hover {
        background: $boost;
    }

    TermWidget:focus {
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
        uri: Node,
        as_datatype: NotLiteralNode = DATATYPES.title,
        triple: Triple | None = None,
        position: TermPositionInTriple | None = None,
        background_color: str | None = None,
    ):
        """Initialize parameters for rendering, navigation, & provenance."""
        self.uri = uri
        self.as_datatype = as_datatype
        self.triple = triple
        self.position_in_triple = position
        self.background_color = background_color
        super().__init__()
        qname = self.app.iolanta.node_as_qname(  # noqa: WPS601
            uri,
        )
        self.renderable = Text(  # noqa: WPS601
            f'⏳ {qname}',
            style='#696969',
        )

        if self.background_color:
            self.styles.background = self.background_color

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
        self.app.action_goto(self.uri)

    def action_provenance(self):
        """Navigate to provenance for the property value."""
        self.app.action_goto(
            TripleURIRef.from_triple(
                subject=self.triple.subject,
                predicate=self.triple.predicate,
                object_=self.triple.object,
            ),
        )

    def on_click(self, event: Click):
        """
        Navigate to the property if we are focused.

        FIXME: Does not work; causes navigation even if not focused.
        """
        if self.has_focus:
            return self.action_goto()

    def on_focus(self):
        """Handle focus state."""
        if self.background_color:
            self.styles.background = 'darkslateblue'

    def on_blur(self):
        """Handle blur state."""
        if self.background_color:
            self.styles.background = self.background_color
