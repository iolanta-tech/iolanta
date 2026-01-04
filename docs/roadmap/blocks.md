---
"@context":
  - "../context.yamlld"
  - owl:inverseOf:
      "@type": "@id"
    rdfs:subPropertyOf:
      "@type": "@id"
owl:inverseOf: https://iolanta.tech/roadmap/is-blocked-by
rdfs:subPropertyOf: http://www.w3.org/ns/prov#wasInformedBy
hide: [toc]
---

# → `roadmap:blocks` <small>property</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Superproperty__

    ---

    [`prov:wasInformedBy`](https://www.w3.org/TR/prov-o/#wasInformedBy)<br/>
    <small>PROV ontology property</small>

-   :material-swap-horizontal:{ .lg .middle } __Inverse Property__

    ---

    [`roadmap:is-blocked-by`](/roadmap/is-blocked-by/)<br/>
    <small>Indicates blocking relationship in reverse direction</small>

-   :material-target-variant:{ .lg .middle } __Purpose__

    ---

    Indicates that one roadmap item blocks another<br/><small>Used to express dependencies and prerequisites</small>

</div>

`roadmap:blocks` indicates that one roadmap item blocks another. It is a subproperty of `prov:wasInformedBy`, allowing blocking relationships to be integrated with provenance tracking.

## Usage

Use `blocks` to express that one item must be completed before another can proceed:

```yaml
- $type: roadmap:Task
  $: Main task
  blocks:
    - $: Dependent task
      $type: roadmap:Task
```

## Inverse Relationship

`roadmap:blocks` is the inverse of `roadmap:is-blocked-by`. If task A blocks task B, then task B is blocked by task A:

```yaml
# These are equivalent:
- $id: _:task-a
  $type: roadmap:Task
  $: Task A
  blocks:
    - _:task-b

- $id: _:task-b
  $type: roadmap:Task
  $: Task B
  is-blocked-by:
    - _:task-a
```

## Nesting

Tasks can be nested directly under `blocks:` for a more compact structure:

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
