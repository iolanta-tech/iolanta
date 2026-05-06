---
title: Load data inside the rdflib SPARQL processor
date: "2024-01-22"
tags: [decision]
---

## Context

The entry point is at `rdflib.graph.Graph.query`.

* It can accept a parsed/compiled `Query` object
    * Seems that it ca be prepared by `rdflib.plugins.sparql.processor.prepareQuery` 
* It can delegate execution to the `store`, as per `use_store_provided` argument
* It delegates processing to `Processor` class

## Decision

Load data directly after parsing the SPARQL query in an `rdflib` SPARQL processor class.

## Consequences

Pro:

* Easy to write.

Contra:

* Will not work for an IRI that is not specified explicitly in the query but retrieved from the graph as a variable. This defies a stand-alone Cyberspace querying command, but is enough for the `iolanta` browser, where most queries explicitly specify the variables.
