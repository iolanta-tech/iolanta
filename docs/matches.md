---
title: iolanta:matches
rdfs:domain: iolanta:Facet
schema:rangeIncludes:
  - rdfs:Literal
hide: [toc]
---

# :material-filter-check: `iolanta:matches` <small>property</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Domain__

    ---

    [`iolanta:Facet`](/Facet/)<br/>
    <small>Iolanta visualization</small>

-   :material-target-variant:{ .lg .middle } __Range (1)__

    ---

    [`rdfs:Literal`](/rdfs/Literal/)<br/><small>SPARQL <code>ASK</code> query</small>

</div>

1.  More features [planned](/roadmap/):
    - [ ] [`rdfs:Resource`](/rdfs/Resource)<br/><small markdown>URL of a file with a SPARQL `ASK` query</small>
    - [ ] [`sh:Shape`](/shacl/Shape)<br/><small markdown>SHACL shape for a node the Facet can visualize</small>

`iolanta:matches` property describes an RDF node that the given Facet can visualize. Currently, the pattern can only be an inline SPARQL `ASK` query. The result of the query is a boolean value. If the query returns `true`, then the Facet is capable of visualizing the node denoted as `$this` in the query.

One Facet might have multiple patterns associated with it.

## Usage Example: Graph Triples visualization

=== "`graph-triples.yamlld`"

    !!! info inline end ""
        :octicons-link-external-24: See the file [on :material-github: GitHub](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/data/graph-triples.yamlld).

    This piece of code defines the facet and describes the shape of the data this facet is capable of visualizing using a SPARQL `ASK` query.

    ```yaml
    --8<-- "iolanta/data/graph-triples.yamlld"
    ```

=== "`context.yaml`"

    !!! info inline end ""
        :octicons-link-external-24: See the file [on :material-github: GitHub](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/data/context.yaml).

    Shared context for YAML-LD descriptions of bundled Iolanta facets. Documents the meaning of the properties used in `graph-triples.yamlld`.
    
    ```yaml
    --8<-- "iolanta/data/context.yaml"
    ```

=== ":material-eye-check-outline: Visualization"
    ```shell
    iolanta https://json-ld.github.io/yaml-ld/spec/data/namespace-prefixes.yamlld
    ```

    By default, every file loaded by Iolanta is treated as an RDF graph, and Graph Triples is configured to be able to visualize RDF Graphs. Voila!

    ![](/screenshots/json-ld.github.io.yaml-ld.spec.data.namespace-prefixes.yamlld.svg)
