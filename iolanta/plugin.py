from __future__ import annotations

import inspect
from abc import ABC
from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from iolanta.models import TripleTemplate

if TYPE_CHECKING:
    from typer import Typer  # noqa: F401

    from iolanta.iolanta import Iolanta


@dataclass
class Plugin(ABC):
    """Base Iolanta plugin."""

    iolanta: Iolanta = field(repr=False)

    @property
    def logger(self) -> Logger:
        return self.iolanta.logger

    @property
    def files_directory(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / "data"

    @property
    def context_path(self) -> Optional[Path]:
        context_path = self.files_directory / "context.yaml"
        if context_path.is_file():
            return context_path

    @property
    def data_files(self) -> Path:
        """Directory containing plugin data files."""
        return self.files_directory

    def retrieve_triple(self, triple_template: TripleTemplate) -> None:
        """Save datasets which might describe the given node into project."""
