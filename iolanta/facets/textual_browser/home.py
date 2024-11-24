from textual.app import ComposeResult
from textual.widgets import Placeholder, Static


class Home(Placeholder):
    """Default home page."""

    def compose(self) -> ComposeResult:
        """
        Show default content.

        TODO: Implement a set of default links, search or something here.
        """
        yield Static('Welcome to Iolanta! This is a placeholder page.')
