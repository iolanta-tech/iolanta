---
is-blocked-by: rdflib-in-cyberspace
title: Use a custom rdflib graph class
---

## Context

RDFLib implements multiple graph classes (such as `Graph`, `Dataset` and others), and also supports multiple storage engines. Where to inject our custom download code?

## Decision

Use a custom graph class.

It would be best to allow using different storage engines (in-memory, BerkeleyDB, Oxigraph, whatever) with our query engine because we basically don't care how the data in local RDF storage is stored, it's enough that we can operate with that data using SPARQL.

Best would be to inject something into SPARQL execution layer, if that's possible.

## Consequences

* We'll be able to use different storage backends
* Upgrade `rdflib` at `iolanta` project to the latest version first
