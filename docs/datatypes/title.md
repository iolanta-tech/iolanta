---
"@context":
  - ../context.yamlld
  - iolanta:hasDefaultFacet:
      "@type": "@id"

$id: https://iolanta.tech/datatypes/title
$type: iolanta:OutputDatatype
$: Title

rdfs:comment: >
  A short string naming something. Used in links, lists, page titles, property tables, and many other cases.

⊆: xsd:string

iolanta:hasDefaultFacet: pkg:pypi/iolanta#title

---

{{ URIRef("https://iolanta.tech/datatypes/title") | as('mkdocs-material-insiders-markdown') }} 
