---
"@context": ../context.yamlld

$id: https://iolanta.tech/mermaid/rdf
$type: iolanta:OutputDatatype
$: RDF Mermaid
iolanta:icon: Ⓜ
hide: toc

⊆: xsd:string

rdfs:comment: >
  Mermaid diagram of every triple in the loaded graph. Uses only data from that
  graph — no external label lookups, no collapsing of `rdfs:label` into node
  text. Literals show lexical values with datatype and language icons; URI nodes
  show bare identifiers; blank nodes show a ⬜ prefix and their identifier;
  annotation triples such as `rdfs:label` and
  `iolanta:icon` appear as ordinary edges.
---

{{ URIRef("https://iolanta.tech/mermaid/rdf") | as('mkdocs-material') }}

## Example

```shell
iolanta path/to/document.yamlld --as mermaid/rdf
```

=== "Diagram"

    ```mermaid
    --8<-- "docs/mermaid/rdf-example.mmd"
    ```

=== "Input"

    ```yaml
    --8<-- "docs/mermaid/rdf-example.yamlld"
    ```
