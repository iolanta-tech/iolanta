from textual.widgets import Label


class Description(Label):
    """Free form textual description."""

    DEFAULT_CSS = """
    Description {
      padding: 1;
      padding-left: 4;
    }
    """  # noqa: WPS115
