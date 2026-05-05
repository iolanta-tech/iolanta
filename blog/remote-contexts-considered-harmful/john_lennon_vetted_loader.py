from pathlib import Path

import yaml
from pyld import FrozenDocumentLoader, jsonld

HERE = Path(__file__).parent

loader = FrozenDocumentLoader(
    documents={
        "https://json-ld.org/contexts/person.jsonld": HERE / "person.jsonld",
        "https://json-ld.org/contexts/dollar-convenience.jsonld": (
            HERE / "dollar-convenience.jsonld"
        ),
    },
)

document = yaml.safe_load((HERE / "john-lennon.yamlld").read_text())

rdf_dataset = jsonld.to_rdf(
    document,
    options={"documentLoader": loader},
)
