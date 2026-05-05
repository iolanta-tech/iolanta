from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class LogLevel(str, Enum):
    """Logging level."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class JsonLines:
    """Streamable JSONL output. Each item becomes one line in the rendered output."""

    lines: Iterable[dict]
