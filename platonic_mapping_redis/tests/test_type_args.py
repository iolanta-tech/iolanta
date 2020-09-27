from platonic_mapping_redis.mapping import RedisDBMapping


class MyMapping(RedisDBMapping[str, int]):
    ...


def test_type_args():
    assert MyMapping().type_args == (str, int)


def test_key_type():
    assert MyMapping().key_type == str


def test_value_type():
    assert MyMapping().value_type == int
