from iolanta.language_flags import language_flag


def test_language_flag_uses_primary_subtag_only():
    assert language_flag("en-GB") == "🇺🇸"
    assert language_flag("en-US") == "🇺🇸"


def test_language_flag_unknown_returns_empty():
    assert language_flag("eo") == ""
    assert language_flag(None) == ""


def test_language_flag_maps_popular_languages():
    assert language_flag("en") == "🇺🇸"
    assert language_flag("ru") == "🇷🇺"
    assert language_flag("uk") == "🇺🇦"
