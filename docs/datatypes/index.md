---
hide: [navigation]
---

# Datatypes

`rdfs:Datatype` is a class describing RDF literal values, for instance,  `xsd:integer` or `rdf:JSON`. Iolanta reuses this concept and attaches Datatypes to **visualizations**. For instance, if [a facet](/facets/) renders some piece of a knowledge graph as a string then it outputs an `xsd:string`.

<div class="grid cards" markdown>

-   :material-format-title:{ .lg .middle } __[Title](title/)__

    ---

    A short string naming something. Used in links, lists, page titles, property tables, and many other cases.


-   :material-format-title:{ .lg .middle } __[Fallback Title](fallback-title/)__

    ---

    Type that only the default, fallback title facet can output. Used to fallback to the default implementation if a more specialized one does not work.

</div>
