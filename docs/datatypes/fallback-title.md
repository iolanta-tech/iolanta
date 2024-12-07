# :material-format-title: Title

<script type="application/ld+json">
  {
    "@context": {
      "rdfs": "https://www.w3.org/2000/01/rdf-schema#",
      "rdf": "https://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "xsd": "https://www.w3.org/2001/XMLSchema#",
      "iolanta": "https://iolanta.tech/",
      "iolanta:hasDefaultFacet": {
        "@type": "@id"
      },
      "rdfs:subClassOf": {
        "@type": "@id"
      }
    },
    "@id": "https://iolanta.tech/datatypes/fallback-title",
    "rdfs:label": "Fallback Title",
    "rdfs:description": "A short string naming something. Used in links, lists, page titles, property tables, and many other cases. Should be used as fallback in case more fine-tuned implementations using https://iolanta.tech/datatypes/title do not work.",
    "rdfs:subClassOf": "xsd:string",
    "@type": "rdfs:Datatype",
    "iolanta:hasDefaultFacet": "python://iolanta.facets.title.TitleFacet"
  }
</script>

A short string naming something. Used in links, lists, page titles, property tables, and many other cases.

!!! warning "This is a fallback datatype"
    Should be used as fallback in case more fine-tuned implementations using [Title](/datatypes/title/) do not work for this IRI.

| Property | Value |
| --- | --- |
| ∈ Instance Of | `rdfs:Datatype` |
| ⊊ Subclass Of | `xsd:string` |
| Has default facet | :material-language-python: `iolanta.facets.title.TitleFacet` | 
