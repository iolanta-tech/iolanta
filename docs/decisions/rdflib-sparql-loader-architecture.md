---
consequences:
  pro:
    - title: Easy to write
  contra:
    - title: Will not work for an IRI, if that is supported, when it is not explicitly specified in the query - but is retrieved from the graph as a variable
      defies:
        title: A stand-alone Cyberspace querying command
      is-enough-for:
        title: Iolanta browser
        because:
          title: Most of our queries are very simple and explicitly specify the variables
---

# Architecture for `rdflib` based Cyberspace SPARQL executor

## Context

The entry point is at `rdflib.graph.Graph.query`.

* It can accept a parsed/compiled `Query` object
    * Seems that it ca be prepared by `rdflib.plugins.sparql.processor.prepareQuery` 
* It can delegate execution to the `store`, as per `use_store_provided` argument
* It delegates processing to `Processor` class

## Decision

Load data directly after parsing the SPARQL query in an `rdflib` SPARQL processor class.
