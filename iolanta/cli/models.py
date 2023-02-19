from enum import Enum


class LogLevel(str, Enum):
    """Logging level."""

    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
