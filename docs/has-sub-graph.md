---
rdfs:domain: iolanta:Graph
schema:rangeIncludes:
  - iolanta:Graph
hide: [toc]
---

# :material-filter-check: `iolanta:has-sub-graph` <small>property</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Domain__

    ---

    [`iolanta:Graph`](/Graph/)<br/>
    <small>RDF Graph</small>

-   :material-target-variant:{ .lg .middle } __Range__

    ---

    [`iolanta:Graph`](/Graph/)<br/><small>RDF Graph</small>

</div>

If one RDF document defines multiple graph (for instance, using `@graph` JSON-LD keyword), Iolanta will import each of these documents as a separate RDF Graph.

`iolanta:has-sub-graph` property will link the parent document graph to each of the graphs that document had created.
