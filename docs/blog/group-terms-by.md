---
title: Group an ontology terms by a property
tags: [decision]
hide:
  - toc
---

## Context

[Ontology](/reference/ontology/) facet displays terms of a given ontology in groups, and we need a method to specify how to group those terms.

## Decision

* Each group in the display should be an `rdfs:Class` which the terms should belong to;
* `owl:Ontology` connects to each class via **a special property**.

## Consequences

* Each grouping class can have an `rdfs:label`, and other properties usable for visualization;
* Not each such class is necessarily a grouping, so the special property we mentioned above will specify which particular classes will be used for the grouping.

## ⇒ Follow-up ADRs

* [Use vann:termGroup for Ontology facet](/blog/use-vann-term-group/)
