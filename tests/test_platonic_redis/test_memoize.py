from platonic.memoize import memoize
from platonic_redis import RedisDBMutableMapping


class UppercaseMapping(RedisDBMutableMapping[str, str]):
    """Doubles stored."""


def test_memoize():
    mapping = UppercaseMapping()
    mapping.clear()

    counter = 0

    @memoize(mapping=mapping)
    def uppercase(v: str) -> str:
        nonlocal counter
        counter += 1
        return v.upper()

    for _ in range(5):
        assert uppercase('foo') == 'FOO'

    assert len(mapping) == 1
    assert set(iter(mapping)) == {'foo', }
    assert counter == 1
