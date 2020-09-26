from dataclasses import dataclass
from functools import cached_property, partial
from typing import (
    Iterator, Callable, TypeVar, MutableMapping, Generic, Mapping,
)

from redis import StrictRedis

KeyType = TypeVar('KeyType', bound=str)
InternalType = TypeVar('InternalType', bound=bytes)
ValueType = TypeVar('ValueType')

bytes_to_string = partial(bytes.decode, encoding='utf-8')
string_to_bytes = str.encode


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

    serialize: InternalToValueType = string_to_bytes  # type: ignore
    deserialize: ValueToInternalType = bytes_to_string  # type: ignore

    def __len__(self) -> int:
        return self.redis.dbsize()

    def __iter__(self) -> Iterator[KeyType]:
        return map(
            bytes_to_string,
            self.redis.scan_iter(),
        )

    def __getitem__(self, k: KeyType) -> ValueType:
        raw_value = self.redis.get(k)

        if raw_value is None:
            raise KeyError(k)

        return self.deserialize(raw_value)


@dataclass
class RedisDBMutableMapping(
    MutableMapping[KeyType, ValueType],
    RedisDBMapping[KeyType, ValueType],
):
    def __setitem__(self, k: KeyType, v: ValueType) -> None:
        self.redis.set(k, self.serialize(v))

    def __delitem__(self, k: KeyType) -> None:
        self.redis.delete(k)

    def clear(self) -> None:
        self.redis.flushdb()
