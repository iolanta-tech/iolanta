---
date: 2025-01-27
title: "Knowledge Graph Design: Iolanta Ontology for Linked Data Visualization"
subtitle: "A foundational knowledge graph design for semantic web browsing and data visualization"
exclude_from_blog: true
hide:
  - navigation
  - toc
---

# Introducing Iolanta ontology<br/><small>Assignment for MC-1 Fall 2025 © Anatoly Scherbakov</small>

## :material-numeric-1-box: Problem & Use Cases

The semantic web contains vast amounts of machine-readable RDF data, but this data is often difficult for humans to understand and navigate.

* **Iolanta** is a tool that aims to provide a uniform way to make Linked Data human friendly,
* which capability is underpinned by the **Iolanta ontology** described in this document.

Use cases we're going to focus on are as follows:

<div class="grid cards" markdown>

-   :material-format-list-bulleted:{ .lg .middle } **Visualize Linked Data**

    ---

    Different output formats require different visualization approaches. Iolanta's facet system adapts rendering based on output datatype, allowing the same data to be rendered as text, HTML, diagrams, or other formats.

-   :material-web:{ .lg .middle } **Browse & Discover Linked Data**

    ---

    Iolanta implements text-based terminal interface to browse Linked Data on the Web.

</div>

## Serialization: YAML-LD

The Iolanta ontology is implemented using [YAML-LD](https://json-ld.github.io/yaml-ld/spec/), a human-friendly serialization format for JSON-LD that makes RDF data more readable and maintainable. Each class and property is defined in separate `.yamlld` files with a shared context, which is provided below.


```yaml title="context.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/context.yamlld"
```

### [`Facet`](/Facet/) <small>class</small>

<div class="grid" markdown>
<div markdown>

```yaml title="facet.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/facet.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (docs / 'blog/knowledge-graph-assignment/facet.yamlld') | as('mermaid') }}
```

</div>
</div>

!!! info "Graph rendering"
    One of the Facets that Iolanta implements is a Mermaid renderer, which was responsible for generation of the graph above. Below, we will look a bit deeper into how that works.


### [`OutputDatatype`](/reference/iolanta/OutputDatatype/) <small>class</small>

<div class="grid" markdown>
<div markdown>

```yaml title="output-datatype.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/output-datatype.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (docs / 'blog/knowledge-graph-assignment/output-datatype.yamlld') | as('mermaid') }}
```

</div>
</div>

### [`SPARQLText`](/reference/iolanta/SPARQLText/) <small>class</small>

<div class="grid" markdown>
<div markdown>

```yaml title="sparql-text.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/sparql-text.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (docs / 'blog/knowledge-graph-assignment/sparql-text.yamlld') | as('mermaid') }}
```

</div>
</div>

### [`matches`](/matches/) <small>datatype property</small>

<div class="grid" markdown>
<div markdown>

```yaml title="matches.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/matches.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (docs / 'blog/knowledge-graph-assignment/matches.yamlld') | as('mermaid') }}
```

</div>
</div>

### [`outputs`](/outputs/) <small>object property</small>

<div class="grid" markdown>
<div markdown>

```yaml title="outputs.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/outputs.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (docs / 'blog/knowledge-graph-assignment/outputs.yamlld') | as('mermaid') }}
```

</div>
</div>

## :material-numeric-3-box: Identifier Strategy

We use slash-terminated URIs under `https://iolanta.tech/` so every resource is dereferenceable to its own page.

### Facet identifiers with Package URL (purl)

Facets use `pkg:` URIs per the [purl spec](https://github.com/package-url/purl-spec).

- Format: `pkg:pypi/<package>#<facet>`
- Examples:
    - `pkg:pypi/iolanta#mermaid-graph` for Mermaid rendering;
    - `pkg:pypi/iolanta#textual-graph` for text user interface graph triple lists;
    - `pkg:pypi/iolanta#title-foaf-person` for the name of a person
- Benefits: unique package-scoped IDs; version-agnostic; standards-based

## :material-numeric-4-box: Graph Representation Choice

Since the domain is Linked Data visualization, we use RDF with OWL semantics, and SPARQL as the query language.

- Native URIs and vocabularies; broad reuse and interoperability.
- LPG is out of scope for this document.

## :material-numeric-5-box: Querying the Knowledge Graph & Visualizing it

There are at least two ways to get a Mermaid representation of the [Facet](#facet-class) class description:

=== "Within an MkDocs page, like this document"

    {% raw %}
    ```jinja2
    {{ (docs / 'blog/knowledge-graph-assignment/facet.yamlld') | as('mermaid') }}
    ```
    {% endraw %}

=== "CLI command"

    ```bash
    iolanta docs/blog/knowledge-graph-assignment/facet.yamlld --as mermaid
    ```

### Stage 0: What is `mermaid` exactly?

It is a shortened form of [https://iolanta.tech/datatypes/mermaid](https://iolanta.tech/datatypes/mermaid), an instance of [`OutputDatatype`](#outputdatatype-class) defined as follows:

<div class="grid" markdown>
<div markdown>

```yaml title="mermaid.yamlld"
--8<-- "iolanta/mermaid/mermaid.yamlld"
```

</div>
<div markdown>

```mermaid
{{ (iolanta / 'iolanta/mermaid/mermaid.yamlld') | as('mermaid') }}
```

</div>
</div>




### Stage 1: Which facets can output a visualization of this `iolanta:OutputDatatype`?

To ascertain that, Iolanta will execute [get-query-to-facet.sparql](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/facets/locator/sparql/get-query-to-facet.sparql) binding `$as_datatype` to `iolanta:mermaid`.

<div class="grid" markdown>
<div markdown>

```sparql
--8<-- "iolanta/facets/locator/sparql/get-query-to-facet.sparql"
```

</div>
<div markdown>
{{ sparql(iolanta / 'iolanta/facets/locator/sparql/get-query-to-facet.sparql', as_datatype=URIRef('https://iolanta.tech/datatypes/mermaid')) }}
</div>
</div>

For each facet returned, Iolanta evaluates its ASK pattern binding `$this` to the target node. The mermaid facet matches with:

<div class="grid" markdown>
<div markdown>

```sparql
--8<-- "iolanta/mermaid/sparql/ask-has-triples.sparql"
```

</div>
<div markdown>

⇒ which evaluates to: {{ sparql(iolanta / 'iolanta/mermaid/sparql/ask-has-triples.sparql', this=path_to_uri(docs / 'blog/knowledge-graph-assignment/facet.yamlld')) }}

</div>
</div>

* This matches because `facet.yamlld` is interpreted by Iolanta as an RDF **named graph** when loading this file;
* We won't delve into `iolanta:has-sub-graph`, that's rather sketchy right now.


### Stage 2: Resolve Facet

We'll not delve into this here, but just to mention:

- The `pkg:` URI has a straightforward mapping to a Python object,
- which is a Python class addressable as `iolanta.mermaid.facet:Mermaid`.

!!! info "Where from is this class?"
    This particular class is bundled with Iolanta, but facet classes can also come with other Python packages — Iolanta plugins.


Here's an abridged version of the class:

```python
class Mermaid(Facet[str]):
    """Mermaid diagram."""

    # …

    def construct_mermaid_for_graph(self, graph: URIRef) -> Iterable[MermaidScalar]:
        """Render graph as mermaid."""
        rows = self.stored_query('graph.sparql', this=graph)
        # …

    def show(self) -> str:
        """Render mermaid diagram."""
        # …
        return str(Diagram(children=[*direct_children, *subgraphs]))
```

Full version: see the [Mermaid facet](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/mermaid/facet.py).

Now, facet class is able to run arbitrary SPARQL queries against the graph, retrieving the information necessary for the visualization.

### Stage 3: Retrieving Graph Data

In particular, the Mermaid facet executes [graph.sparql](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/mermaid/sparql/graph.sparql) to fetch all triples in the named graph, substituting `$this` to the URI of `facet.yamlld`:

```sparql title="graph.sparql"
--8<-- "iolanta/mermaid/sparql/graph.sparql"
```

<details markdown>
<summary>Triples for <code>facet.yamlld</code> (too many of them)</summary>

{{ sparql(iolanta / 'iolanta/mermaid/sparql/graph.sparql', this=path_to_uri(docs / 'blog/knowledge-graph-assignment/facet.yamlld')) }}

</details>

These triples are formatted as Mermaid nodes and edges by the facet, producing the diagram, which:

* Either gets printed in the console, and you can save it to a file or copy it,
* Or embedded into software which Iolanta is working with.

## Other examples

<div class="grid cards" markdown>

-   #### An ORCID profile

    [![](/screenshots/orcid.org.0000-0002-1825-0097.svg)](/screenshots/orcid.org.0000-0002-1825-0097.svg)

    ```bash
    iolanta https://orcid.org/0000-0002-1825-0097
    ```

-   #### RDFS label

    [![](/screenshots/www.w3.org.2000.01.rdf-schema.svg)](/screenshots/www.w3.org.2000.01.rdf-schema.svg)

    ```bash
    iolanta https://www.w3.org/2000/01/rdf-schema#label
    ```

-   #### OWL vocabulary terms

    [![](/screenshots/owl.svg)](/screenshots/owl.svg)

    ```bash
    iolanta https://www.w3.org/2002/07/owl#
    ```

</div>

While rendering Linked Data, Iolanta will try to fetch references from the Web to other pieces of Linked Data. Thus, we are trying to get the most complete visualization.

## Conclusion

The Iolanta ontology provides a framework for Linked Data visualization and browsing with:

- Clear domain focus on semantic web usability
- Well-structured RDF/OWL implementation  
- Professional URI strategy following Linked Data best practices
- Full SPARQL support with real-world applications
- Integration with existing semantic web resources
