---
title: Download data transparently
is-blocked-by: find-data-source-by-triple-template
$id: download-data-transparently
---

## Context

When asking for triples in a graph, an application might encounter no results, which might mean that there is not enough information available in the graph.

## Decision

Transparently try to find the missing triples on the Matrix before returning results of the query. Add triples and rerun the query to see if information had been obtained.

## Consequences

Plugin or application writers will have full illusion of querying the whole Matrix instead of their local graph, which is exactly what we want to achieve.
