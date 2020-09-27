import pytest

from platonic_mapping_redis.mapping import (
    RedisDBMutableMapping,
)


class TestMapping(RedisDBMutableMapping[str, str]):
    """My test mapping."""


@pytest.fixture(scope='module')
def mapping():
    mapping = TestMapping(
        url='redis://localhost:6379/0'
    )

    mapping.clear()

    yield mapping

    mapping.close()


def test_nit_picking(mapping: RedisDBMutableMapping[str, str]):
    mapping.clear()
    mapping['site-name'] = 'John Connor'
    assert len(mapping) == 1
    assert mapping['site-name'] == 'John Connor'
    del mapping['site-name']


def test_iteration(mapping: RedisDBMutableMapping[str, str]):
    mapping['T1'] = 'T-800'
    mapping['T3'] = 'T-X'

    assert len(mapping) == 2

    assert set(iter(mapping)) == {'T1', 'T3'}
