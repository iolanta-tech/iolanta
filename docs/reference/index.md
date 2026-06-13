---
hide: [toc, navigation]
---

# :octicons-book-24: Reference

## Tools

<div class="grid cards" markdown>

-   :octicons-terminal-24: __[`iolanta` CLI](/reference/cli/)__

    ---

    Command line interface for rendering Linked Data resources, queries, search
    results, and Jinja2 Markdown templates.

-   :material-code-braces: __[`--render-template` macros & variables](/reference/render-template-macros-and-variables/)__

    ---

    Template macros and variables available when rendering Jinja2 Markdown with
    `iolanta --render-template`.

</div>

## Iolanta Ontology

<div class="grid cards" markdown>

-   👁 __[`iolanta:Facet`](/Facet/)__
    
    ---
    
    RDFS class for Iolanta Facets — the magic things which visualize pieces of Linked Data in Iolanta.

-   ▤ __[`iolanta:OutputDatatype`](/reference/iolanta/OutputDatatype/)__
    
    ---
    
    Output format where visualization applications render their results.

-   `{}` __[`iolanta:SPARQLText`](/reference/iolanta/SPARQLText/)__
    
    ---
    
    A datatype for representing SPARQL query text.

-   ▾ __[`iolanta:matches`](/matches/)__
    
    ---
    
    Describe what kind of nodes a given Facet can visualize.


-   ⊂ __[`iolanta:has-sub-graph`](/has-sub-graph/)__
    
    ---
    
    Links an RDF Graph representing a document to each other RDF Graph that was parsed from said document.

-   ≼ __[`iolanta:is-preferred-over`](/is-preferred-over/)__
    
    ---
    
    Specify that one Facet is cooler than the other.


-   🖼️ __[`iolanta:icon`](/icon/)__
    
    ---
    
    Attach a Unicode symbol that Iolanta can use as a compact visual marker for a resource.


-   → __[`iolanta:outputs`](/outputs/)__
    
    ---
    
    Specify the [datatype](/reference/rdf/datatype) of the visualization a given Facet produces.


-   📛 __[`iolanta:when-no-facet-found`](/when-no-facet-found/)__
    
    ---
    
    What if no facet is found to visualize this node for a given [datatype](/reference/rdf/datatype)? Specify an emergency facet to use in such cases.


-   👁 __[`iolanta:visualizes`](/visualizes/)__
    
    ---
    
    Link a nanopublication assertion to the ontology whose visualization metadata it carries — used to discover community-published groupings at render time.

</div>

## Ontologies Iolanta relies upon

<div class="grid cards" markdown>

-   :material-eye-check-outline: __[RDF](/reference/rdf/)__
    
    ---
    
    RDF vocabulary (`rdf:`): properties, classes, lists, and literals.

-   :material-eye-check-outline: __[RDFS](/reference/rdfs/)__
    
    ---
    
    RDF Schema (`rdfs:`): classes and properties for lightweight ontologies.

</div>
