import inspect
from abc import ABC
from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import List, Optional

from rdflib.term import Node
from typer import Typer


@dataclass
class Plugin(ABC):
    """Base Iolanta plugin."""

    iolanta: 'iolanta.Iolanta' = field(repr=False)

    @property
    def logger(self) -> Logger:
        return self.iolanta.logger

    @property
    def typer_app(self) -> Optional[Typer]:
        """Typer app for this plugin's CLI."""
        return None

    @property
    def files_directory(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / 'data'

    @property
    def context_path(self) -> Optional[Path]:
        if (context_path := self.files_directory / 'context.yaml').is_file():
            return context_path

    @property
    def data_files(self):
        return self.files_directory

    def retrieve(self, node: Node) -> List[Path]:
        """Save datasets which might describe the given node into project."""
        return []
