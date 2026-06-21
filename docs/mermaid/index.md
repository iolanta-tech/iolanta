---
title: Mermaid
hide: [toc]
---

# Ⓜ Mermaid <small>Plugin</small>

!!! info "Bundled with `iolanta`"

The Mermaid plugin renders RDF graphs as [Mermaid](https://mermaid.js.org/) diagram syntax. It is the generic graph visualization layer that other bundled features can build on, including the [Roadmap plugin](/roadmap/).

## Example

```shell
iolanta example.yamlld --as mermaid
```

```mermaid
{{ (docs / 'mermaid/example.yamlld') | as('mermaid') }}
```

## Renderers

The plugin outputs [`https://iolanta.tech/datatypes/mermaid`](/datatypes/mermaid/), an `iolanta:OutputDatatype` for Mermaid diagram syntax.

Roadmap rendering specializes this output datatype as [`https://iolanta.tech/roadmap/datatypes/mermaid`](/roadmap/), so generic graph diagrams and roadmap diagrams remain separate render targets.

## Related Facets

<div class="grid cards" markdown>

-   Ⓜ __`pkg:pypi/iolanta#mermaid-graph`__

    ---

    Generic RDF graph renderer for `https://iolanta.tech/datatypes/mermaid`.

-   Ⓜ __`pkg:pypi/iolanta#mermaid-rdf`__

    ---

    Exact RDF triple renderer for `https://iolanta.tech/mermaid/rdf`.

-   ◌ __`pkg:pypi/iolanta#mermaid-nanopublication`__

    ---

    Specialized Mermaid renderer for nanopublications.


</div>
