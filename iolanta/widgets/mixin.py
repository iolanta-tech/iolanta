from iolanta.iolanta import Iolanta


class IolantaWidgetMixin:
    """Mixin for any Iolanta-powered Textual widget."""

    @property
    def iolanta(self) -> Iolanta:
        """Iolanta instance."""
        return self.app.iolanta    # type: ignore
