from dataclasses import dataclass, field
from functools import cached_property
from typing import (
    Iterator, Callable, TypeVar, MutableMapping, Type,
)

from redis import StrictRedis

from platonic import generic_type_args, const
from platonic_mapping.mapping import PlatonicMapping
from typecasts import DefaultTypecasts
from typecasts.main import Typecasts

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
    PlatonicMapping[KeyType, ValueType],
):
    """Redis-backed mapping based on a collection."""

    internal_type: type = bytes
    typecasts: Typecasts = field(default_factory=const(DefaultTypecasts))

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
