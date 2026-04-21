from pathlib import Path
import json
import pyld.jsonld as jsonld

VETTED_CONTEXTS = {
    "https://json-ld.org/contexts/person.jsonld": (
        Path(__file__).parent / "person.jsonld"
    ),
    "https://json-ld.org/contexts/dollar-convenience.jsonld": (
        Path(__file__).parent / "dollar-convenience.jsonld"
    ),
}


def cached_loader(url, options):
    if url in VETTED_CONTEXTS:
        path = VETTED_CONTEXTS[url]
        return {
            "contentType": "application/ld+json",
            "contextUrl": None,
            "documentUrl": url,
            "document": json.loads(path.read_text()),
        }
    raise ValueError(f"Refusing to fetch un-vetted context: {url}")


jsonld.set_document_loader(cached_loader)
