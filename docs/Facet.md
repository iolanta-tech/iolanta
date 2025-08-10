---
hide: [toc]
---

# :material-eye-check-outline: `Facet`

*Facet* is a visualization. It is a piece of program code that processes a given RDF node and its context, the whole graph, and draws a visualization of a certain type.

![](/assets/facet.png)


In RDF, a facet is referenced by an IRI: this way, Linked Data can tell Iolanta how it can be visualized.

| Facet Type                                | In RDF                            | In Code                                             |
|-------------------------------------------|-----------------------------------|-----------------------------------------------------|
| Python based facet                        | `pkg:pypi/some-pypi-package#facet-name` | Python class, inherited from `iolanta.facets.Facet` |

More types are [planned](/roadmap) (1).
{ .annotate }

1.  In particular, WASM based facets downloadable from the Web and executed in a sandbox.

## Facets

For now, the only facets that Iolanta supports are bundled with it.

<div class="grid cards" markdown>

-   :octicons-eye-24: __[`TitleFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/title/facets.py)__
    
    ---
    
    Render a human readable title for a node.

    * URI: `pkg:pypi/iolanta#title`
    * Outputs: [string](/reference/xsd/string/)


- :octicons-eye-24: __[`Class`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_class/facets.py)__
    
    ---
    
    For an RDFS or OWL `Class`, render a list of its instances that we know about.

    * URI: `pkg:pypi/iolanta#textual-classFacet` 
    * Outputs: [Textual widget](/cli/textual/)

  
- :octicons-eye-24: __[`TextualDefaultFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_default/facets.py)__
    
    ---
    
    All RDF properties and their values for a given node in interactive textual UI. *(Not best naming though.)*

    * URI: `pkg:pypi/iolanta#textual-properties`
    * Outputs: [Textual widget](/cli/textual/)


  
- :octicons-eye-24: __[`GraphFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_graph/facets.py)__
    
    ---
    
    For an RDF graph, list triples that it contains.

    * URI: `pkg:pypi/iolanta#textual-graph`
    * Outputs: [Textual widget](/cli/textual/)

  
- :octicons-eye-24: __[`NanopublicationFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_nanopublication/facet.py)__
    
    ---
    
    Display contents of a [Nanopublication](/reference/np/Nanopublication/).

    * URI: `pkg:pypi/iolanta#textual-nanopublication`
    * Outputs: [Textual widget](/cli/textual/)

 
- :octicons-eye-24: __[`OntologyFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_ontology/facets.py)__
    
    ---
    
    Display terms of an [Ontology](/reference/owl/ontology/).

    * URI: `pkg:pypi/iolanta#textual-ontology`
    * Outputs: [Textual widget](/cli/textual/)

 
- :octicons-eye-24: __[`TextualPropertyPairsTableFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_property_pairs_table.py)__
    
    ---
    
    Display Subject → Object pairs for an RDF [Property](/reference/rdf/property/).

    * URI: `pkg:pypi/iolanta#textual-property-pairs`
    * Outputs: [Textual widget](/cli/textual/)
 
 
- :material-github: __[Ideas for more?](https://github.com/iolanta-tech/iolanta/issues/)__
    
    ---
    
    Feel free to ➕ add an issue!

</div>
