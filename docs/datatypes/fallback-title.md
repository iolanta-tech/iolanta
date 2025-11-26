---
"@context":
  - ../context.yamlld
  - iolanta:hasDefaultFacet:
      "@type": "@id"

$id: https://iolanta.tech/datatypes/fallback-title
$type: iolanta:OutputDatatype
$: Fallback Title

rdfs:comment: >
  A short string naming something. Used in links, lists, page titles, property tables, and many other cases.
  Should be used as fallback in case more fine-tuned implementations using https://iolanta.tech/datatypes/title do not work.

⊆: xsd:string

iolanta:hasDefaultFacet: pkg:pypi/iolanta#title
---

{{ URIRef("https://iolanta.tech/datatypes/fallback-title") | as('mkdocs-material-insiders-markdown') }} 
