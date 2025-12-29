---
"@context":
  "@import": https://json-ld.org/contexts/dollar-convenience.jsonld
  schema: https://schema.org/
  rdfs: http://www.w3.org/2000/01/rdf-schema#
  wd: https://www.wikidata.org/entity/

  named-after:
    "@id": wd:P138
    "@type": "@id"
  
  schema:author:
    "@type": "@id"
  
  schema:character:
    "@type": "@id"
  
  schema:containedInPlace:
    "@type": "@id"
  
  appears-in:
    "@reverse": schema:character
    "@type": "@id"

$id: https://www.wikidata.org/entity/Q24229338
$type:
  - schema:Place
  - https://www.wikidata.org/entity/Q3240715
schema:containedInPlace: https://www.wikidata.org/entity/Q405
schema:description: A lunar crater.

named-after:
  $type: schema:Person
  rdfs:label: Rhysling
  schema:description: A fictional character.
  schema:alternateName: Noisy
  appears-in:
    $type: https://www.wikidata.org/entity/Q49084
    rdfs:label: The Green Hills of Earth
    schema:author: https://www.wikidata.org/entity/Q123078
---

Rhysling crater on the Moon was named after the fictional character Rhysling, also known as Noisy, from Robert A. Heinlein's short story "The Green Hills of Earth".
