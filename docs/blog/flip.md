---
date: 2024-10-04
title: Flip
---

## Context

I need to flip between facets when looking at the same node.

A few changes needed for that.

```mermaid
graph TD
    env-to-type("<code>environment</code> → <code>rdf:Datatype</code>") --> subtypes("Subtypes<br/><em>Anything there already?</em>") --> generic("Generic types")
    subtypes --> dependent("Dependent/parametric types") --> propagate("Propagate params downward?") 
    env-to-type --- no-viewpoints("Viewpoints<br/>no longer needed!")
    subtypes --> json("Use <code>rdf:JSON</code>!")
    subtypes --> mro("Multiple inheritance?")
    
    subtypes --> widget("<code>TextualWidget</code>")
    click widget "https://textual.textualize.io/guide/widgets/"
    
    widget --"is supertype of"-->full-screen("<code>TextualFullScreenWidget</code>")
    
    full-screen --> downward("Target type: search downward")
    full-screen --> upward("hasInstanceFacet: search upward<br/>or just rely upon OWL")
    
    env-to-type --> facet-url("URL encapsulating the facet to use") --> flip("[f] Flip menu")
    facet-url --> facet-parameters("How does facet know rendering/type params???")
    facet-parameters --> table("Want to render countries as table")
    table --> viewpoint("Table is a viewpoint node, we render it")
    table --> table-type("Table is a type")
    
```

## Decision

* [ ] Create and call a Flip page to list all applicable facets
* [ ] Run specific facet on click
* [ ] And then work on env → type migration
