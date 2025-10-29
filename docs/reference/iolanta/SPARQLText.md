---
rdfs:domain: iolanta:SPARQLText
rdfs:range: rdfs:Datatype
hide: [toc]
---

# :material-code-braces: `iolanta:SPARQLText` <small>class</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Superclass__

    ---

    [`rdfs:Datatype`](/rdfs/Datatype/)<br/>
    <small>RDF Schema datatype</small>

-   :material-target-variant:{ .lg .middle } __Purpose__

    ---

    A datatype for representing SPARQL query text<br/><small>Enables semantic validation and tooling</small>

</div>

`iolanta:SPARQLText` is a custom datatype for representing SPARQL query text. This allows for semantic validation and tooling specific to SPARQL syntax.

## Usage

The `iolanta:matches` property uses `iolanta:SPARQLText` to specify SPARQL ASK queries:

```yaml
$id: iolanta:matches
rdfs:range: iolanta:SPARQLText
```

This enables:
- **Syntax validation** of SPARQL queries
- **Tooling support** for query editing and debugging
- **Semantic understanding** of query patterns
- **Type safety** in RDF processing

## Examples

```sparql
ASK WHERE { ?instance a $this }
ASK WHERE { GRAPH $this { ?s ?p ?o } }
ASK WHERE { ?subject $this ?object }
```
