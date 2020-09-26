from typing import TypeVar


T = TypeVar('T')


def identity(anything: T) -> T:
    """Identity function."""
    return anything
