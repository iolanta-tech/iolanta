from rdflib import URIRef
from textual.widgets import Static
from textual.worker import Worker, WorkerState

from iolanta.iolanta import Iolanta
from iolanta.models import NotLiteralNode


class PageTitle(Static):
    """Iolanta page title."""

    DEFAULT_CSS = """
    PageTitle {
        padding: 1;
        background: darkslateblue;
        color: white;
        text-style: bold;
    }
    """

    def __init__(self, iri: NotLiteralNode) -> None:
        """Initialize."""
        self.iri = iri
        qname = self.iolanta.node_as_qname(iri)
        super().__init__(qname)

    @property
    def iolanta(self) -> Iolanta:
        """Iolanta instance."""
        return self.app.iolanta

    def construct_title(self):
        """Render the title via Iolanta in a thread."""
        return self.iolanta.render(
            self.iri,
            environments=[URIRef('https://iolanta.tech/env/title')],
        )[0]

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
                self.renderable = title
                self.refresh()

            case WorkerState.ERROR:
                raise ValueError(event)
