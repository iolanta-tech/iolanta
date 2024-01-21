---
is-blocked-by: download-data-transparently
---

## Context

We already know that at least one triple template is needed to choose the source from where we will fetch the triples for this template. However, the interaction between software and the Cyberspace is probably going to be in SPARQL. Should we invent a new triple template based API for this?

## Alternatives

* Dynamically resolve data sources while executing a SPARQL query,
* Do so with Triple Fragments,
* Or do so with a sort of ad hoc RDF API.

## Decision

We shall use SPARQL.

The review of literature attached to this ADR (see [state-of-the-art.yaml](state-of-the-art.yaml)) reveals that certain developments in this area do exist, including:

* `LAV` system,
* Its SPARQL based `SemLAV` extension,
* and parallel extensions to `SemLAV`.

## Consequences

* Use SPARQL as basic language to query the Cyberspace
* Resolve parts of SPARQL query against different data sources (or RDF Views if that might be said)
* Multiple triples might come from one data source and can be joined into one query

