"""Flag emoji for RDF language tags."""

LANGUAGE_FLAGS: dict[str, str] = {
    "ar": "🇸🇦",
    "de": "🇩🇪",
    "en": "🇺🇸",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "hi": "🇮🇳",
    "hy": "🇦🇲",
    "am": "🇦🇲",
    "it": "🇮🇹",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "nl": "🇳🇱",
    "pl": "🇵🇱",
    "pt": "🇵🇹",
    "ru": "🇷🇺",
    "sv": "🇸🇪",
    "tr": "🇹🇷",
    "ua": "🇺🇦",
    "zh": "🇨🇳",
}


def language_flag(language_tag: str | None) -> str:
    """Return a flag emoji for the primary BCP 47 language subtag."""
    if not language_tag:
        return ""

    primary_language = language_tag.split("-", maxsplit=1)[0].lower()
    return LANGUAGE_FLAGS.get(primary_language, "")
