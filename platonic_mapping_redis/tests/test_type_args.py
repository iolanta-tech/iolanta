from platonic import generic_type_args
from platonic_mapping_redis.mapping import RedisDBMapping


class MyMapping(RedisDBMapping[str, int]):
    ...


def test_type_args():
    assert generic_type_args(MyMapping()) == (str, int)


def test_key_type():
    assert MyMapping().key_type == str


def test_value_type():
    assert MyMapping().value_type == int
