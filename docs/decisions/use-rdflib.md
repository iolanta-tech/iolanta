---
title: Use rdflib for querying the Cyberspace
$id: rdflib-in-cyberspace
---

## Context

Multiple tools are available to federatively query the Cyberspace: Jena, Virtuoso, ...

## Decision

Use `rdflib` as one

* Written in Python
* Supporting multiple storage engines and graph types
* Used in `iolanta`
* Most familiar to me

## Consequences

* Upgrade `rdflib` in `iolanta` project to the latest version first
* And then see how to inject dynamic data source resolve and download into that
