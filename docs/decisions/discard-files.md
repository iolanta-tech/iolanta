---
title: Discard files, just use a cache
---

## Context

When loading data from the Web dynamically we can use plain `graph.parse()` method. Downloading files onto disk explicitly is not strictly necessary for the `iolanta` browser experience. We'll get back to that when we start editing Linked Data.

## Decision

`shelve` the graph, load data into it. This is enough for an MVP.

## Consequences

Get into reproducibility and file-based LD repos later.
