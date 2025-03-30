from textual.widgets import Static
from textual.worker import Worker, WorkerState

from iolanta.models import NotLiteralNode
from iolanta.namespaces import DATATYPES
from iolanta.widgets.mixin import IolantaWidgetMixin


class PageTitle(IolantaWidgetMixin, Static):
    """Iolanta page title."""

    DEFAULT_CSS = """
    PageTitle {
        padding: 1;
        background: darkslateblue;
        color: white;
        text-style: bold;
    }
    """

    def __init__(self, iri: NotLiteralNode, extra=None) -> None:
        """Initialize."""
        self.iri = iri
        self.extra = extra
        super().__init__(iri)

    def construct_title(self):
        """Render the title via Iolanta in a thread."""
        return self.iolanta.render(
            self.iri,
            as_datatype=DATATYPES.title,
        )

    def on_mount(self):
        """Initialize rendering of a title."""
        self.run_worker(self.construct_title, thread=True)

    def on_worker_state_changed(   # noqa: WPS210
        self,
        event: Worker.StateChanged,
    ):
        """Render title when generated."""
        match event.state:
            case WorkerState.SUCCESS:
                title = event.worker.result
                if self.extra:
                    title = f'{title} {self.extra}'
                self.update(title)

            case WorkerState.ERROR:
                raise ValueError(event)
