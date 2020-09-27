from dataclasses import dataclass
from functools import cached_property, partial
from typing import (
    Iterator, Callable, TypeVar, MutableMapping, Generic, Mapping, get_args,
    Type,
)

from redis import StrictRedis

from typecasts import DefaultTypecasts

KeyType = TypeVar('KeyType')
ValueType = TypeVar('ValueType')
InternalType = TypeVar('InternalType', bound=bytes)


@dataclass
class RedisMixin:
    """Redis connection details."""
    url: str = 'redis://localhost:6379/0'

    @cached_property
    def redis(self) -> StrictRedis:
        # FIXME Closing of this connection is not guaranteed. Need to look.
        return StrictRedis.from_url(self.url)

    def close(self) -> None:
        self.redis.close()


InternalToValueType = Callable[[InternalType], ValueType]
ValueToInternalType = Callable[[ValueType], InternalType]


@dataclass
class RedisDBMapping(
    RedisMixin,
    Mapping[KeyType, ValueType],
    Generic[KeyType, ValueType],
):
    """Redis-backed mapping based on a collection."""

    internal_type: type = bytes

    @cached_property
    def type_args(self):
        for parent in self.__orig_bases__:  # type: ignore  # noqa: WPS609
            type_args = get_args(parent)
            if type_args:
                return type_args

        return ()

    @cached_property
    def key_type(self) -> Type[KeyType]:
        return self.type_args[0]

    @cached_property
    def value_type(self) -> Type[ValueType]:
        return self.type_args[1]

    @cached_property
    def serialize_key(self) -> Callable[[KeyType], InternalType]:
        return DefaultTypecasts[self.key_type, self.internal_type]

    @cached_property
    def deserialize_key(self) -> Callable[[InternalType], KeyType]:
        return DefaultTypecasts[self.internal_type, self.key_type]

    @cached_property
    def serialize_value(self) -> Callable[[ValueType], InternalType]:
        return DefaultTypecasts[self.value_type, self.internal_type]

    @cached_property
    def deserialize_value(self) -> Callable[[InternalType], ValueType]:
        return DefaultTypecasts[self.internal_type, self.value_type]

    def __len__(self) -> int:
        return self.redis.dbsize()

    def __iter__(self) -> Iterator[KeyType]:
        return map(
            self.deserialize_key,
            self.redis.scan_iter(),
        )

    def __getitem__(self, k: KeyType) -> ValueType:
        raw_value = self.redis.get(k)

        if raw_value is None:
            raise KeyError(k)

        return self.deserialize_value(raw_value)


@dataclass
class RedisDBMutableMapping(
    MutableMapping[KeyType, ValueType],
    RedisDBMapping[KeyType, ValueType],
):
    def __setitem__(self, k: KeyType, v: ValueType) -> None:
        self.redis.set(k, self.serialize_value(v))

    def __delitem__(self, k: KeyType) -> None:
        self.redis.delete(self.serialize_key(k))

    def clear(self) -> None:
        self.redis.flushdb()
