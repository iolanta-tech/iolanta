---
hide: [toc]
---

# :material-eye-check-outline: `Facet`

*Facet* is a visualization. It is a piece of program code that processes a given RDF node and its context, the whole graph, and draws a visualization of a certain type.

![](/assets/facet.png)


In RDF, a facet is referenced by an IRI: this way, Linked Data can tell Iolanta how it can be visualized.

| Facet Type                                | In RDF                            | In Code                                             |
|-------------------------------------------|-----------------------------------|-----------------------------------------------------|
| Python based facet                        | `python://some_module.FacetClass` | Python class, inherited from `iolanta.facets.Facet` |

More types are [planned](/roadmap) (1).
{ .annotate }

1.  In particular, WASM based facets downloadable from the Web and executed in a sandbox.

## Facets

For now, the only facets that Iolanta supports are bundled with it.

<div class="grid cards" markdown>

-   :octicons-eye-24: __[`TitleFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/title/facets.py)__
    
    ---
    
    Render a human readable title for a node.

    * URI: `python://iolanta.facets.title.TitleFacet`
    * Outputs: [string](/reference/xsd/string/)


- :octicons-eye-24: __[`Class`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_class/facets.py)__
    
    ---
    
    For an RDFS or OWL `Class`, render a list of its instances that we know about.

    * URI: `python://iolanta.facets.textual_class.ClassFacet` 
    * Outputs: [Textual widget](/cli/textual/)

  
- :octicons-eye-24: __[`TextualDefaultFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_default/facets.py)__
    
    ---
    
    All RDF properties and their values for a given node in interactive textual UI. *(Not best naming though.)*

    * URI: `python://iolanta.facets.textual_default.TextualDefaultFacet`
    * Outputs: [Textual widget](/cli/textual/)


  
- :octicons-eye-24: __[`GraphFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_graph/facets.py)__
    
    ---
    
    For an RDF graph, list triples that it contains.

    * URI: `python://iolanta.facets.textual_graph.GraphFacet`
    * Outputs: [Textual widget](/cli/textual/)

  
- :octicons-eye-24: __[`NanopublicationFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_nanopublication/facet.py)__
    
    ---
    
    Display contents of a [Nanopublication](/reference/np/Nanopublication/).

    * URI: `python://iolanta.facets.textual_nanopublication.NanopublicationFacet`
    * Outputs: [Textual widget](/cli/textual/)

 
- :octicons-eye-24: __[`OntologyFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_ontology/facets.py)__
    
    ---
    
    Display terms of an [Ontology](/reference/owl/ontology/).

    * URI: `python://iolanta.facets.textual_ontology.OntologyFacet`
    * Outputs: [Textual widget](/cli/textual/)

 
- :octicons-eye-24: __[`TextualPropertyPairsTableFacet`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/textual_property_pairs_table.py)__
    
    ---
    
    Display Subject → Object pairs for an RDF [Property](/reference/rdf/property/).

    * URI: `python://iolanta.facets.textual_property_pairs_table.TextualPropertyPairsTableFacet`
    * Outputs: [Textual widget](/cli/textual/)
 
 
- :material-github: __[Ideas for more?](https://github.com/iolanta-tech/iolanta/issues/)__
    
    ---
    
    Feel free to ➕ add an issue!

</div>
