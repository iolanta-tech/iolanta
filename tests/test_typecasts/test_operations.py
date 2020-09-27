from typing import NewType

import pytest

from typecasts import DefaultTypecasts, identity
from typecasts.main import Typecasts
from typecasts.errors import TypecastNotFound, RedundantIdentity


class MyType:
    """My little brave class."""


def test_identity():
    assert Typecasts()[float, float] == identity
    assert Typecasts()[MyType, MyType] == identity


def test_not_found():
    with pytest.raises(TypecastNotFound):
        _ = Typecasts()[str, int]


def test_set_item():
    typecasts = Typecasts()
    typecasts[int, str] = str
    assert typecasts[int, str] == str


def test_redundant_identity():
    with pytest.raises(RedundantIdentity):
        Typecasts()[int, int] = identity
