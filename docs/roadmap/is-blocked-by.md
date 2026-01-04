---
"@context":
  - "../context.yamlld"
  - owl:inverseOf:
      "@type": "@id"
    rdfs:subPropertyOf:
      "@type": "@id"
owl:inverseOf: https://iolanta.tech/roadmap/blocks
rdfs:subPropertyOf: http://www.w3.org/ns/prov#wasInformedBy
hide: [toc]
---

# ← `roadmap:is-blocked-by` <small>property</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Superproperty__

    ---

    [`prov:wasInformedBy`](https://www.w3.org/TR/prov-o/#wasInformedBy)<br/>
    <small>PROV ontology property</small>

-   :material-swap-horizontal:{ .lg .middle } __Inverse Property__

    ---

    [`roadmap:blocks`](/roadmap/blocks/)<br/>
    <small>Indicates blocking relationship in forward direction</small>

-   :material-target-variant:{ .lg .middle } __Purpose__

    ---

    Indicates that one roadmap item is blocked by another<br/><small>Used to express dependencies from the dependent item's perspective</small>

</div>

`roadmap:is-blocked-by` indicates that one roadmap item is blocked by another. It is a subproperty of `prov:wasInformedBy`, allowing blocking relationships to be integrated with provenance tracking.

## Usage

Use `is-blocked-by` to express dependencies from the perspective of the dependent item:

```yaml
- $id: _:task-b
  $type: roadmap:Task
  $: Task B
  is-blocked-by:
    - _:task-a
```

## Inverse Relationship

`roadmap:is-blocked-by` is the inverse of `roadmap:blocks`. If task A blocks task B, then task B is blocked by task A:

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

Tasks can be nested directly under `is-blocked-by:` for a more compact structure:

```yaml
- $type: roadmap:Task
  $: Dependent task
  is-blocked-by:
    - $: Prerequisite 1
      $type: roadmap:Task
    - $: Prerequisite 2
      $type: roadmap:Task
```
