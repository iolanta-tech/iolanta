---
title: Use bottom menu to flip facets
date: 2024-10-13
overrides: flip.md
---

## Context

We need some way to flip from one facet to another, regardless of the implementation of the facet itself.

## Decision

Display alternative facets in the bottom menu.

## Consequences

### Pro

* Easy to implement, no extra widgets needed

### Contra

* Might be too many facets there
  * There are not that many facets right now, we do not care so far
  * Later we can expand this to a special menu or whatever
