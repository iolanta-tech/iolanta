# :material-format-title: Title

<script type="application/ld+json">
  {
    "@context": {
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
      "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "xsd": "http://www.w3.org/2001/XMLSchema#",
      "iolanta": "https://iolanta.tech/",
      "iolanta:hasDefaultFacet": {
        "@type": "@id"
      },
      "rdfs:subClassOf": {
        "@type": "@id"
      }
    },
    "@id": "https://iolanta.tech/datatypes/title",
    "rdfs:label": "Title",
    "rdfs:description": "A short string naming something. Used in links, lists, page titles, property tables, and many other cases.",
    "rdfs:subClassOf": "xsd:string",
    "@type": "rdfs:Datatype",
    "iolanta:hasDefaultFacet": "python://iolanta.facets.title.TitleFacet"
  }
</script>

A short string naming something. Used in links, lists, page titles, property tables, and many other cases.

| Property | Value |
| --- | --- |
| ∈ Instance Of | `rdfs:Datatype` |
| ⊊ Subclass Of | `xsd:string` |
| Has default facet | :material-language-python: `iolanta.facets.title.TitleFacet` | 
