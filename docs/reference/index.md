---
hide: [toc, navigation]
---

# :octicons-book-24: Reference

## Iolanta Vocabulary

<div class="grid cards" markdown>

-   :material-eye-check-outline: __[`iolanta:Facet`](/Facet/)__
    
    ---
    
    RDFS class for Iolanta Facets — the magic things which visualize pieces of Linked Data in Iolanta.

-   :material-format-list-bulleted: __[`iolanta:OutputDatatype`](/reference/iolanta/OutputDatatype/)__
    
    ---
    
    Output format where visualization applications render their results.

-   :material-code-braces: __[`iolanta:SPARQLText`](/reference/iolanta/SPARQLText/)__
    
    ---
    
    A datatype for representing SPARQL query text.

-   :material-filter-check: __[`iolanta:matches`](/matches/)__
    
    ---
    
    Describe what kind of nodes a given Facet can visualize.


-   :material-filter-check: __[`iolanta:has-sub-graph`](/has-sub-graph/)__
    
    ---
    
    Links an RDF Graph representing a document to each other RDF Graph that was parsed from said document.

-   ≼ __[`iolanta:is-preferred-over`](/is-preferred-over/)__
    
    ---
    
    Specify that one Facet is cooler than the other.


-   → __[`iolanta:outputs`](/outputs/)__
    
    ---
    
    Specify the [datatype](/reference/rdf/datatype) of the visualization a given Facet produces.


-   📛 __[`iolanta:when-no-facet-found`](/when-no-facet-found/)__
    
    ---
    
    What if no facet is found to visualize this node for a given [datatype](/reference/rdf/datatype)? Specify an emergency facet to use in such cases.

</div>
