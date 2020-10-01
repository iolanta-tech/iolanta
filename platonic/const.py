from typing import Callable, TypeVar

T = TypeVar('T')


def const(anything: T) -> Callable[[], T]:
    """Generate a function which always returns the same value."""
    return lambda: anything
