---
title: Use vann:termGroup for Ontology facet
tags: [decision]
hide:
  - toc
---

<small markdown>[Group an ontology terms by a property](/blog/group-terms-by/) ⇒</small>

# Use `vann:termGroup` for [Ontology](/reference/ontology/) facet

## Context

We need to choose a property to connect an `owl:Ontology` to each `rdfs:Class` which groups its terms.

## Decision

Use [`vann:termGroup`](https://vocab.org/vann/) as a property that explicitly does what we need. I did not find anything besides that at [LOV](https://lov.linkeddata.es/).

## Consequences

We will use an existing vocabulary and not invent bicycles.
