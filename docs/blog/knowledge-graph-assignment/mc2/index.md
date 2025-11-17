---
date: 2025-01-27
title: "Knowledge Graph Design: Extending Iolanta Ontology"
subtitle: "Building with confidence - modularity, time/space, entities, and queries"
exclude_from_blog: true
hide:
  - navigation
  - toc
---

# Extending Iolanta ontology<br/><small>Assignment for MC-2 Fall 2025 © Anatoly Scherbakov</small>

This is a continuation of [MC-1](/blog/knowledge-graph-assignment/), where the Iolanta ontology was introduced. MC-2 elaborates on a few aspects of how Iolanta works.

## :material-numeric-1-box: Modularizing a KG

### Named Graphs

Iolanta loads every source of Linked Data, be it a file on local disk or a URI of such file on the Web, into a separate **Named Graph** in the **RDF Dataset** that Iolanta maintains, in-memory, relying upon [`rdflib`](https://github.com/RDFLib/rdflib).

[RDF Graph Literals and Named Graphs](https://www.w3.org/2009/07/NamedGraph.html) is an Editor's Draft, but it very conveniently defines `rdfg:Graph` as a class for Named Graphs. That does not mean that every Named Graph will be automatically assigned this class using `rdf:type`, but it is a convenient endpoint to which we can connect a facet. Like this:

```yaml title="textual_graphs.yamlld"
--8<-- "iolanta/facets/textual_graphs/data/textual_graphs.yamlld"
```

The `pkg:pypi/iolanta#textual-graphs` facet is using the following SPARQL query to find graphs:

```sparql title="textual-graphs.sparql"
--8<-- "iolanta/facets/textual_graphs/sparql/graphs.sparql"
```

And that's how this looks in Iolanta CLI (Command Line Interface):

```shell
iolanta http://www.w3.org/2009/rdfg#Graph
```

[![](/screenshots/www.w3.org.2009.rdfg.svg)](/screenshots/www.w3.org.2009.rdfg.svg)

We called Iolanta to visualize only the `rdfg:Graph` node, but it imported a number of other things (like, YAML-LD files bundled with Iolanta itself), and that's how many Named Graphs have been created by the system.

### Default Graph

Is a `UNION` of all Named Graphs. Iolanta relies upon `rdflib` supporting this capability. This greatly simplifies all SPARQL queries that facets have to run.

### Foundational Ontology

We rely upon `rdfs:label`, `rdfs:subClassOf`, et cetera, and we try to keep Iolanta ontology very minimal.

## :material-numeric-2-box: Time and Space

### Time

There is a separate Named Graph with Iolanta RDF Dataset denoted as `iolanta://_meta`. Let's view it.

```shell
iolanta iolanta://_meta
```

[![](/screenshots/_meta..svg)](/screenshots/_meta..svg)

The triples in this graph record times when each of the other Named Graphs was loaded. This is important because Iolanta has a capability to auto reload a file in the project directory when that file is edited. This metadata store helps keep track of whether each Named Graph is in sync with its source on disk.

The `iolanta:last-loaded-time` property is used to record these timestamps:

<div class="grid" markdown>
<div markdown>

```yaml title="last-updated-time.yamlld"
--8<-- "docs/blog/knowledge-graph-assignment/mc2/last-updated-time.yamlld"
```

</div>

<div markdown>

```shell
iolanta last-updated-time.yamlld
```

[![](/screenshots/docs.blog.knowledge-graph-assignment.mc2.last-updated-time.yamlld.svg)](/screenshots/docs.blog.knowledge-graph-assignment.mc2.last-updated-time.yamlld.svg)

</div>
</div>

### Space

Iolanta does not provide any special treatment to space-describing ontologies at this moment, but that can be implemented in specialized facets.

For instance, based on a pair of WGS84 coordinates, an Iolanta facet could generate HTML and JS code for an OpenStreetMap widget which then could be embedded into a publication. 

## :material-numeric-3-box: Groups of Entities

Enforcement of OWL rules, such as

* `owl:oneOf`,
* or `owl:Restriction`,

requires the support of OWL reasoning. Iolanta is designed so that it does not require any inference at all.

We can, however, use Iolanta to visualize these properties themselves. Why not?

<div class="grid" markdown>
<div markdown>

:material-link-variant: [`owl:oneOf`](http://www.w3.org/2002/07/owl#oneOf)

```shell
iolanta http://www.w3.org/2002/07/owl#oneOf
```

[![](/screenshots/www.w3.org.2002.07.owl.oneof.svg)](/screenshots/www.w3.org.2002.07.owl.oneof.svg)

</div>

<div markdown>

:material-link-variant: [`owl:Restriction`](http://www.w3.org/2002/07/owl#Restriction)

```shell
iolanta http://www.w3.org/2002/07/owl#Restriction
```

[![](/screenshots/www.w3.org.2002.07.owl.restriction.svg)](/screenshots/www.w3.org.2002.07.owl.restriction.svg)

</div>
</div>


## :material-numeric-4-box: Graph Queries

<div class="grid cards" markdown>

-   :material-check-circle:{ .lg .middle } __SELECT__

    ---

    ✅ Used to choose facets, and used by facets themselves, there are examples in **MC-1** and in this document as well

-   :material-check-circle:{ .lg .middle } __ASK__

    ---

    ✅ Used for facet pattern matching

-   :material-check-circle:{ .lg .middle } __CONSTRUCT__

    ---

    ✅ Can be used if facet needs that

-   :material-close-circle:{ .lg .middle } __INSERT__

    ---

    ❌ Not used, facets cannot modify the graph

-   :material-close-circle:{ .lg .middle } __UPDATE__

    ---

    ❌ Not used, facets cannot modify the graph

-   :material-close-circle:{ .lg .middle } __DELETE__

    ---

    ❌ Not used, facets cannot modify the graph

-   :material-close-circle:{ .lg .middle } __DESCRIBE__

    ---

    ❌ Not used

</div>

## :material-numeric-5-box: RDF vs LPGs

Iolanta's domain is explicitly visualization of RDF data, not of LPGs. This is a crucial choice because Iolanta means to visualize data based on their *meaning*.

* With RDF, URIs make it possible: you know how to use `rdfs:label`, for example, in whichever context it may appear;
* With LPGs, the idea of Iolanta would be scarcely implementable at all.
