import dataclasses

import pytest

from errorclass import errorclass


def test_no_parens():
    @errorclass
    class WrongAnswer:
        """{self.answer} is wrong!"""

        answer: int

    assert WrongAnswer.__annotations__ == {'answer': int}
    assert WrongAnswer.__doc__ == '{self.answer} is wrong!'

    assert dataclasses.is_dataclass(WrongAnswer)
    assert issubclass(WrongAnswer, Exception)
    assert WrongAnswer(answer=5).answer == 5
    assert str(WrongAnswer(answer=5)) == '5 is wrong!'

    with pytest.raises(WrongAnswer):
        raise WrongAnswer(answer=13)


def test_from_scratch():
    """Construct and test an ad-hoc dataclass-powered Exception."""
    @dataclasses.dataclass
    class ColorError(Exception):
        """I hate {color} color!"""

        color: str

        def __str__(self):
            return self.__doc__.format(**dataclasses.asdict(self))

    err = ColorError(color='red')

    assert str(err) == 'I hate red color!'

    with pytest.raises(ColorError) as raised_error:
        raise err

    # noinspection Mypy
    assert str(raised_error.value) == 'I hate red color!'
