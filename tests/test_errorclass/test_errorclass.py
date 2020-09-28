import dataclasses

import pytest

from docerror import DocError


def test_no_parens():
    @dataclasses.dataclass
    class WrongAnswer(DocError):
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
