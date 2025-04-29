---
hide: [toc]
---

# → `iolanta:outputs`


<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Domain__

    ---

    [`iolanta:Facet`](/Facet/)<br/>
    <small>Iolanta visualization</small>

-   :material-target-variant:{ .lg .middle } __Range__

    ---

    [`rdfs:Datatype`](/reference/rdfs/datatype/)<br/>
    <small>Datatype of the value the facet returns</small>

</div>

Facets return visualizations. If we were to save a visualization as a node into an RDF graph, that would be a [Literal](/reference/rdfs/literal); and a Literal would have a [Datatype](/reference/rdfs/datatype/) associated with it.

We leverage it to describe types of visualizations. In different contexts, we might want different datatypes. For instance, if [a facet](/facets/) renders some piece of a knowledge graph as a string then it outputs an `xsd:string`.

<div class="grid cards" markdown>

-   :material-format-title:{ .lg .middle } __[Title](title/)__

    ---

    A short string naming something. Used in links, lists, page titles, property tables, and many other cases.


-   :material-format-title:{ .lg .middle } __[Fallback Title](fallback-title/)__

    ---

    Type that only the default, fallback title facet can output. Used to fallback to the default implementation if a more specialized one does not work.

</div>
