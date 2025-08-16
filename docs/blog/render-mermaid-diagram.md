---
title: Render Mermaid diagram in MkDocs using "as" filter
date: "2025-08-16"
hide: [toc]
tags: [decision]
---

# Render Mermaid diagram in MkDocs using `…|as('mermaid')` filter

## Context

We have a YAML-LD file, called `yaml-ld.yamlld`, in our Mkdocs directory. We need to render it as a Mermaid diagram and insert into a page using `mkdocs-macros-plugin`. What syntax should we use?

### Customization

If we are going to do any customization of the diagram, we will do that in YAML-LD, not in the page itself.

### Alternatives

=== ":white_check_mark: `…|as('mermaid')` filter"

    {% raw %}
    ```jinja2
    {{ "yaml-ld.yamlld"|as('mermaid') }}
    ```
    {% endraw %}
    <div class="grid" markdown>
    <div markdown>
    ### :heavy_plus_sign: Pro
    
    * Still simple syntax
    * Is reusable in other contexts
    </div>
    <div markdown>
    ### :heavy_minus_sign: Contra
    * Might be more complicated to use
    </div>
    </div>
    

=== ":red_square: `mermaid(…)` function"

    {% raw %}
    ```jinja2
    {{ mermaid("yaml-ld.yamlld") }}
    ```
    {% endraw %}
    <div class="grid" markdown>
    <div markdown>
    ### :heavy_plus_sign: Pro
    
    * Simple syntax
    </div>
    <div markdown>
    ### :heavy_minus_sign: Contra
    * No control over the diagram
    * Necessity to invent a new function for each new visualization beyond Mermaid
    </div>
    </div>

=== ":red_square: `…|mermaid` filter"

    {% raw %}
    ```jinja2
    {{ "yaml-ld.yamlld"|mermaid }}
    ```
    {% endraw %}
    <div class="grid" markdown>
    <div markdown>
    ### :heavy_plus_sign: Pro
    
    * Simple syntax
    </div>
    <div markdown>
    ### :heavy_minus_sign: Contra
    * No control over the diagram
    * Necessity to invent a new filter for each new visualization beyond Mermaid
    </div>
    </div>

## Example

```mermaid
{{ (docs / 'howto/nanopublish/yaml-ld.yamlld') | as('mermaid') }}
```
