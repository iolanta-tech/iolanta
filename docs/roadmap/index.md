---
title: Roadmap
hide:
  - toc
  - navigation
---

# :octicons-project-roadmap-24: Roadmap <small>Plugin</small>


!!! info "Bundled with `iolanta` ⩾ 2.1.12"


<div class="tabbed-set tabbed-alternate" data-tabs="1:2">
<input checked="checked" id="__tabbed_1_1" name="__tabbed_1" type="radio" />
<input id="__tabbed_1_2" name="__tabbed_1" type="radio" />
<div class="tabbed-labels">
<label for="__tabbed_1_1">Iolanta development roadmap</label>
<label for="__tabbed_1_2">YAML-LD Source Code</label>
</div>
<div class="tabbed-content">
<div class="tabbed-block" markdown>

```shell
iolanta iolanta-development-roadmap.yamlld --as https://iolanta.tech/roadmap/datatypes/mermaid
```

```mermaid
{{ (docs / 'roadmap/iolanta-development-roadmap.yamlld') | as('https://iolanta.tech/roadmap/datatypes/mermaid') }}
```

</div>
<div class="tabbed-block" markdown>

```yaml title="iolanta-development-roadmap.yamlld (top 20 lines)"
--8<-- "docs/roadmap/iolanta-development-roadmap.yamlld:1:20"
# …
```

</div>
</div>
</div>

## Quick Start

To use the Roadmap plugin in your roadmap files, import the context:

```yaml
"@context": https://iolanta.tech/roadmap/contexts/v0.1.yamlld
```

This context provides the namespace prefixes and property mappings you need to write roadmap data.

### Minimal Example

```yaml
"@context": https://iolanta.tech/roadmap/contexts/v0.1.yamlld

$included:
  - $id: _:complete-docs
    $type: roadmap:Task
    $: Complete documentation
    blocks:
      - $: Publish release
        $type: roadmap:Task
```

### Nesting Tasks

Tasks can be nested directly under `blocks:` or `is-blocked-by:` properties. This creates a more compact and readable structure:

```yaml
- $type: roadmap:Task
  $: Main task
  blocks:
    - $: Subtask 1
      $type: roadmap:Task
    - $: Subtask 2
      $type: roadmap:Task
      blocks:
        - $: Nested subtask
          $type: roadmap:Task
```

### Identifiers

When you need to reference a roadmap item from another item (using `blocks` or `is-blocked-by`), you must give it an identifier using `$id`. In roadmap files, identifiers should be **blank nodes** using the `_:` prefix:

- ✅ Good: `$id: _:implement-auth`
- ❌ Bad: `$id: roadmap:task-1` (full URI not needed for local references)

If an item is not referenced anywhere else in your roadmap, you don't need to provide an `$id` at all. You only need an identifier when:
- The item is referenced from elsewhere (e.g., `blocks: [_:some-task]`)
- The item needs to be referenced later in the file

## Data Model

The Roadmap plugin uses the following classes and properties:

<div class="grid cards" markdown>

-   :octicons-tasklist-24: __[`roadmap:Task`](/roadmap/Task/)__

    ---

    A to-do item or feature<br/><small>Subclass of `prov:Activity`</small>

-   :octicons-bug-24: __[`roadmap:Bug`](/roadmap/Bug/)__

    ---

    A known issue<br/><small>Subclass of `roadmap:Task`</small>

-   :octicons-calendar-24: __[`roadmap:Event`](/roadmap/Event/)__

    ---

    A scheduled event or milestone<br/><small>Subclass of `prov:Activity`</small>

-   → __[`roadmap:blocks`](/roadmap/blocks/)__

    ---

    Indicates that one item blocks another<br/><small>Inverse of `roadmap:is-blocked-by`, subproperty of `prov:wasInformedBy`</small>

-   ← __[`roadmap:is-blocked-by`](/roadmap/is-blocked-by/)__

    ---

    Indicates that one item is blocked by another<br/><small>Inverse of `roadmap:blocks`, subproperty of `prov:wasInformedBy`</small>

</div>

### Relationship to PROV Ontology

The roadmap vocabulary builds on the [PROV ontology](https://www.w3.org/TR/prov-o/) (`prov:Activity`, `prov:wasInformedBy`), allowing roadmap items to be integrated with provenance tracking and activity descriptions.

## Rendering

### Command Line

Render a roadmap file as a Mermaid diagram:

```shell
iolanta path/to/roadmap.yamlld --as https://iolanta.tech/roadmap/datatypes/mermaid
```

### In MkDocs

Use the Iolanta template to render roadmaps in your documentation:

{% raw %}
```jinja2
{{ (docs / 'path/to/roadmap.yamlld') | as('https://iolanta.tech/roadmap/datatypes/mermaid') }}
```
{% endraw %}

### Exporting to Images

Generate PNG or SVG images from your roadmap for use in blogs, documentation, or presentations:

```shell
# Generate PNG
iolanta path/to/roadmap.yamlld --as https://iolanta.tech/roadmap/datatypes/mermaid | mmdc -i - -o roadmap.png

# Generate SVG
iolanta path/to/roadmap.yamlld --as https://iolanta.tech/roadmap/datatypes/mermaid | mmdc -i - -o roadmap.svg -b transparent
```

This requires [`@mermaid-js/mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) to be installed. Install it with:

```shell
npm install -g @mermaid-js/mermaid-cli
```

## Context Versioning

The roadmap context is versioned to ensure stability. Current version:

- **v0.1**: `https://iolanta.tech/roadmap/contexts/v0.1.yamlld`

When referencing the context, pin to a specific version (e.g., `v0.1`) for stability.

Future versions will be published at `https://iolanta.tech/roadmap/contexts/v<version>.yamlld`.
