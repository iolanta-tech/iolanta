from typing import NewType

import pytest

from typecasts import DefaultTypecasts, identity
from typecasts.main import Typecasts, TypecastNotFound


class MyType:
    """My little brave class."""


def test_identity():
    assert Typecasts()[float, float] == identity
    assert Typecasts()[MyType, MyType] == identity


def test_not_found():
    with pytest.raises(TypecastNotFound):
        _ = Typecasts()[str, int]
