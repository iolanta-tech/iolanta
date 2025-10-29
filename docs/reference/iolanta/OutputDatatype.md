---
rdfs:domain: iolanta:OutputDatatype
rdfs:range: rdfs:Datatype
hide: [toc]
---

# :material-format-list-bulleted: `iolanta:OutputDatatype` <small>class</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Superclass__

    ---

    [`rdfs:Datatype`](/rdfs/Datatype/)<br/>
    <small>RDF Schema datatype</small>

-   :material-target-variant:{ .lg .middle } __Purpose__

    ---

    Output format where visualization applications render their results<br/><small>Examples: terminal text, HTML, Mermaid diagrams</small>

</div>

`iolanta:OutputDatatype` represents the output format where visualization applications render their results. This class is a subclass of `rdfs:Datatype` and defines the various formats that Iolanta facets can produce.

## Examples

- **Terminal Text**: `https://iolanta.tech/cli/textual`
- **HTML**: `https://iolanta.tech/datatypes/html`
- **Mermaid Diagrams**: `https://iolanta.tech/datatypes/mermaid`
- **Icons**: `https://iolanta.tech/datatypes/icon`

## Usage

Facets specify which output datatypes they support using the `iolanta:outputs` property:

```yaml
$id: pkg:pypi/iolanta#textual-graph
iolanta:outputs: https://iolanta.tech/cli/textual
```

This allows Iolanta to select appropriate facets based on the desired output format.
