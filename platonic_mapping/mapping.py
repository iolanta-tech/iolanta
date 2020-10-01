from abc import ABC
from functools import cached_property
from typing import TypeVar, Mapping, Generic, Type, Callable

from platonic import generic_type_args
from typecasts import DefaultTypecasts
from typecasts.main import Typecasts

KeyType = TypeVar('KeyType')
ValueType = TypeVar('ValueType')
InternalType = TypeVar('InternalType')


class PlatonicMapping(
    Mapping[KeyType, ValueType],
    ABC,
):
    """Abstract Mapping definition."""
    internal_type: type
    typecasts: Typecasts

    @cached_property
    def key_type(self) -> Type[KeyType]:
        return generic_type_args(self)[0]

    @cached_property
    def value_type(self) -> Type[ValueType]:
        return generic_type_args(self)[1]

    @cached_property
    def serialize_key(self) -> Callable[[KeyType], InternalType]:
        return self.typecasts[self.key_type, self.internal_type]

    @cached_property
    def deserialize_key(self) -> Callable[[InternalType], KeyType]:
        return self.typecasts[self.internal_type, self.key_type]

    @cached_property
    def serialize_value(self) -> Callable[[ValueType], InternalType]:
        return self.typecasts[self.value_type, self.internal_type]

    @cached_property
    def deserialize_value(self) -> Callable[[InternalType], ValueType]:
        return self.typecasts[self.internal_type, self.value_type]
