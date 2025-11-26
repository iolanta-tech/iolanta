---
"@context":
  - ../context.yamlld
  - iolanta:hasDefaultFacet:
      "@type": "@id"
    iolanta:hasInstanceFacet:
      "@type": "@id"

$id: https://iolanta.tech/datatypes/title
$type: iolanta:OutputDatatype
$: Title

rdfs:comment: >
  A short string naming something. Used in links, lists, page titles, property tables, and many other cases.

⊆: xsd:string

iolanta:hasDefaultFacet: pkg:pypi/iolanta#title

"@included":
  "@id": foaf:Person
  iolanta:hasInstanceFacet:
    "@id": pkg:pypi/iolanta#title-foaf-person
    →: https://iolanta.tech/datatypes/title
---

{{ URIRef("https://iolanta.tech/datatypes/title") | as('mkdocs-material-insiders-markdown') }} 
