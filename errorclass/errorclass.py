from dataclasses import dataclass, asdict
from typing import Type, TypeVar

T = TypeVar('T')


@dataclass
class BaseErrorClass(Exception):
    """"""
    def __str__(self):
        return self.__doc__.format(self=self)


def errorclass(cls: Type[T]) -> Type[BaseErrorClass]:
    """Dataclasses for Python exceptions."""
    exception_cls = type(
        cls.__name__,
        (
            cls,
            BaseErrorClass,
        ),
        {
            '__annotations__': cls.__annotations__,
            '__doc__': cls.__doc__
        }
    )
    return dataclass(exception_cls, repr=False)
