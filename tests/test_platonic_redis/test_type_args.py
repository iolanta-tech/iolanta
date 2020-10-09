from platonic import generic_type_args
from platonic_redis import RedisDBMapping, RedisDBMutableMapping


class MyMapping(RedisDBMapping[str, int]):
    ...


def test_type_args():
    assert generic_type_args(MyMapping()) == (str, int)


def test_key_type():
    assert MyMapping().key_type == str


def test_value_type():
    assert MyMapping().value_type == int


def test_instantiation_without_inheritance():
    instance = RedisDBMutableMapping[str, int]()
    assert instance.key_type == str
    assert instance.value_type == int
