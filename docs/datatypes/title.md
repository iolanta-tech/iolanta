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
      },
      "foaf": "https://xmlns.com/foaf/0.1/"
    },
    "@id": "https://iolanta.tech/datatypes/title",
    "rdfs:label": "Title",
    "rdfs:description": "A short string naming something. Used in links, lists, page titles, property tables, and many other cases.",
    "rdfs:subClassOf": "xsd:string",
    "@type": "rdfs:Datatype",
    "iolanta:hasDefaultFacet": "python://iolanta.facets.title.TitleFacet",
    "@included": {
        "@id": "foaf:Person",
        "iolanta:hasInstanceFacet": {
            "@id": "python://iolanta.facets.foaf_person_title.FOAFPersonTitle",    
            "iolanta:outputs": {
              "@id": "https://iolanta.tech/datatypes/title"    
            }    
        }
    }
}
</script>

A short string naming something. Used in links, lists, page titles, property tables, and many other cases.

| Property           | Value                                                        |
|-------------------|--------------------------------------------------------------|
| ∈ Instance Of     | `rdfs:Datatype`                                              |
| ⊊ Subclass Of     | `xsd:string`                                                 |
| Has default facet | :material-language-python: `iolanta.facets.title.TitleFacet` | 


## Specialized Facets

| Class         | Facet                                                       | Description                                            |
|---------------|-------------------------------------------------------------|--------------------------------------------------------|
| `foaf:Person` | `python://iolanta.facets.foaf_person_title.FOAFPersonTitle` | Render name of a person from their first and last name | 
