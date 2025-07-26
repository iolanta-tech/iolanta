from rich.markdown import Markdown
from textual.containers import VerticalScroll
from textual.widgets import Label


class Description(VerticalScroll):
    """Free form textual description."""

    DEFAULT_CSS = """
    Description {
      padding: 4;
      padding-top: 1;
      padding-bottom: 1;
      max-height: 100%;
    }
    """  # noqa: WPS115

    def __init__(self, renderable: str | Markdown):
        """
        Initialize a Description widget with a renderable content.

        Args:
            renderable: Content to display, either as a string or
                Markdown object
        """
        self.renderable = renderable
        super().__init__()

    def compose(self):
        """Build and return the widget's component structure."""
        yield Label(self.renderable)
