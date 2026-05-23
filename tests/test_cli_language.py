import importlib

import pytest

from iolanta.cli import main as cli_main


def _c_utf8_locale():
    return ("C.UTF-8", "UTF-8")


@pytest.mark.parametrize(
    ("locale_name", "expected_language"),
    [
        (None, "en"),  # noqa: WPS226
        ("C", "en"),
        ("C.UTF-8", "en"),
        ("POSIX", "en"),
        ("en_US", "en"),
        ("de_DE.UTF-8", "de"),
    ],
)
def test_default_language(locale_name: str | None, expected_language: str):
    assert (  # noqa: WPS437
        cli_main._default_language(locale_name) == expected_language
    )


def test_default_from_posix_locale(monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(
            cli_main.locale,
            "getlocale",
            _c_utf8_locale,
        )
        reloaded_cli_main = importlib.reload(cli_main)

    assert reloaded_cli_main.DEFAULT_LANGUAGE == "en"
    importlib.reload(cli_main)
