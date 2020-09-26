from iolanta.app import memoize
from platonic_mapping_redis.mapping import RedisDBMutableMapping


# FIXME this causes the system to fail. I need to determine the serialize
#   and deserialize functions depending on types.
class DoublesMapping(RedisDBMutableMapping[int, int]):
    """Doubles stored."""

    serialize = bytes
    deserialize = int


def test_memoize():
    mapping = DoublesMapping()

    @memoize(mapping=mapping)
    def multiply(v: int) -> int:
        return 2 * v

    assert multiply(1) == 2
    assert multiply(-1) == -2

    assert len(mapping) == 2
