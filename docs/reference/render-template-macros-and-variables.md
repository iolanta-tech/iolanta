---
title: "`--render-template` macros & variables"
hide: [toc]
---

# `--render-template` macros & variables

`iolanta --render-template` renders a Jinja2 Markdown file and prints the
rendered Markdown to stdout.

This page documents the Iolanta-specific macros and variables available inside
those templates.

## Macros

{% raw %}
| Macro | Syntax | Purpose |
| --- | --- | --- |
| `as` | `{{ node | as("datatype") }}` | Render a node, path, or IRI through Iolanta as the requested datatype. |
| `uri` | `{{ value | uri }}` | Convert a path, string, or `URIRef` to `URIRef`. |
| `sparql(...)` | `{{ sparql("query.sparql", name=value) }}` | Execute a document-relative SPARQL file and return a Markdown table. |
| `path_to_uri(...)` | `{{ path_to_uri(path) }}` | Convert a path to a file IRI. |
{% endraw %}

## Variables

| Variable | Value |
| --- | --- |
| `docs` | The template file's parent directory. |
| `iolanta` | The template file's parent directory in the current v1 API. |
| `URIRef` | The rdflib `URIRef` constructor. |

## Examples

Render a document-relative YAML-LD file as Mermaid:

{% raw %}
```jinja2
{{ "diagram.yamlld" | as("mermaid") }}
```
{% endraw %}

Render an explicit IRI as a title:

{% raw %}
```jinja2
{{ URIRef("https://example.org/alice") | as("title") }}
```
{% endraw %}

Run a SPARQL query file and insert its Markdown table output:

{% raw %}
```jinja2
{{ sparql("queries/labels.sparql", iri=URIRef("https://example.org/alice")) }}
```
{% endraw %}

Convert a document-relative path to a URI:

{% raw %}
```jinja2
{{ "data/alice.yamlld" | uri }}
```
{% endraw %}

## Boundary

This is the supported `--render-template` surface. Normal Jinja2 syntax is
available, but only the Iolanta-specific macros and variables documented here
are promised.

MkDocs macros are a separate integration. MkDocs-only macros such as
`colored_bytes` are not available in `--render-template`.
