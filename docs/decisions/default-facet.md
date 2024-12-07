---
title: Use Record as a default facet
---

## Context

Presently, when I'm trying to render something, `Link` is the default facet.

```shell
$ iolanta render rdfs:comment
https://www.w3.org/2000/01/rdf-schema#comment
```

## Decision

Use Record instead.

## Consequences

This will make the default rendering much more useful for debugging the graph.
