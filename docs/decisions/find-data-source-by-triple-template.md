---
title: Find data source by a triple template
$id: find-data-source-by-triple-template
---

## Context

* We are trying to render `rdf:type`, and we cannot see its `rdfs:label`. To solve this, it is enough to download `rdf` ontology, and the address of that ontology is hidden within the `rdf:type` URL.
* We want to render `rdf:type` with a label in Russian language; if Russian labels for RDF terms are stored in a separate file then we need to know
  * that we need an `rdfs:label`,
  * and we need to know that language must be `@ru`.

## Decision

A function that determines the location of new data must know full triple template that we're trying to interpolate against the graph.

## Consequences

* Analyse `…` package as a possible alternative
* Implement `.find_triple()` method for a `Facet`.
