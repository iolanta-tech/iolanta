import functools
from typing import TypeVar, MutableMapping, Callable

KeyType = TypeVar('KeyType')
ValueType = TypeVar('ValueType')


def memoize(
    mapping: MutableMapping[KeyType, ValueType],
):
    """Cache the responses of the given function in the mapping."""
    def _decorator(func: Callable[[KeyType], ValueType]):
        @functools.wraps(func)
        def wrapper(key: KeyType) -> ValueType:
            try:
                return mapping[key]

            except KeyError:
                calculated_value = func(key)
                mapping[key] = calculated_value
                return calculated_value

        return wrapper

    return _decorator
