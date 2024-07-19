---
title: Parse JSON-LD with pyld library
tags: [decision]
date: 2024-07-19
hide: [toc]
---

# Parse JSON-LD with [:material-github: `digitalbazaar/pyld`](https://github.com/digitalbazaar/pyld)

## Context

We need to parse JSON-LD files from the Web and local filesystems.

| Alternative | Contra |
| --- | --- |
| Use `rdflib`'s native JSON-LD parser | `rdflib` is planning to switch to `pyld`: [:material-github: `rdflib/rdflib#2308`](https://github.com/RDFLib/rdflib/issues/2308) |
| Use `pyld` via `rdflib` when `rdflib` does the transition | Will take some time, I suppose |
| Call `pyld` by hand and feed results → `rdflib` | ∅ |

## Decision

Call `pyld` by hand and feed results → `rdflib`

## Consequences

* When `rdflib` switches to use `pyld` we will be able to simplify our code.
