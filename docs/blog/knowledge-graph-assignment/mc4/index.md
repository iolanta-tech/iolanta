---
date: 2025-01-27
title: "Knowledge Graph Design: Building Something Real"
subtitle: "Reflections on technical and business considerations in enterprise knowledge graphs"
exclude_from_blog: true
hide:
  - navigation
  - toc
---

# Building Something Real<br/><small>Assignment for MC-4 Fall 2025 © Anatoly Scherbakov</small>

This document synthesizes technical and business considerations for building knowledge graphs in real-world enterprise contexts.

## :material-numeric-1-box: Big Picture Understanding: Technical and Business Considerations Combined

I first found out about the Semantic Web maybe around 2013, when I was a university student. I played a little bit with RDF, SPARQL, and with a :simple-php: PHP triple store that supported them (I think the up to date version of that product is now known as [:simple-github: `semsol/arc2`](https://github.com/semsol/arc2)).

Since then, time to time, I returned to this topic as a detour from my software development career. I had a few ideas about what to do, did some learning, prototypes and experiments. That went rather slowly though.

![Linked Data Visualization book cover](data_visualization_book_cover.jpg){ align="right" width="250px" }

Then, at one point, I read the book:

> *Linked Data Visualization: Techniques, Tools and Big Data* by Laura Po, Nikos Bikakis, Federico Desimoni, and George Papastefanatos (Morgan & Claypool, 2020), ISBN: 9781681737256, [linkeddatavisualization.com](https://www.linkeddatavisualization.com/)

I noticed that, even though the book analyzes a bunch of RDF visualization tools, none of them have been used to build tables, graphs, charts, lists in *the book itself*.

This hinted that there is a general issue with converting a piece of RDF into something a human can easily view.

<br clear="both" />

[Fresnel vocabulary](https://www.w3.org/2005/04/fresnel-info/) was one attempt to solve the issue. It seems to be a little bit constraining though. Particular type of visualizations are tied to particular RDF terms from the vocabulary; Fresnel is coupled with HTML and CSS. What if we want to visualize data not in HTML but, say, in the terminal? Or in 3D?

I thought something more generic, which would allow using an arbitrary piece of code (known henceforth as a `Facet`) to render Linked Data in a certain fashion, would be interesting to implement. So I did; I started working on this iteration of Iolanta in January 2023.

I implemented facets, terms, and a rudimentary ontology, built a website, but… it is a frustrating experience to have a technology and search for use cases where it can be applied. 

I feel the KGC Course helped me change my perspective.

## :material-numeric-2-box: Application to Work, Projects, and Real-World Situations

Going through the course was one particular use case for Iolanta — not just because its ontology was the subject matter but also because I used it to prepare the papers for the course extensively. Particular parts of the course motivated development of particular features.

<div class="grid cards" markdown>

-   [**MC-**:material-numeric-1-circle:{ .lg .middle }](/blog/knowledge-graph-assignment/)

    ---

    - Mermaid rendering facet (`pkg:pypi/iolanta#mermaid-graph`)
    - [`SPARQLText`](/reference/iolanta/SPARQLText/) class for storing SPARQL queries as Linked Data
    - [`OutputDatatype`](/reference/iolanta/OutputDatatype/) class for defining output formats
    - [MkDocs macros plugin](https://github.com/fralau/mkdocs-macros-plugin) integration (`as()` filter, `sparql()` macro, `path_to_uri()` macro)

-   [**MC-**:material-numeric-2-circle:{ .lg .middle }](/blog/knowledge-graph-assignment/mc2/)

    ---

    - Graphs visualization for the textual UI (`pkg:pypi/iolanta#textual-graphs`), to list all named graphs
    - [`iolanta:last-loaded-time`](/blog/knowledge-graph-assignment/mc2/last-updated-time.yamlld) property for tracking when named graphs were loaded
    - `iolanta://_meta` special named graph for metadata tracking

-   [**MC-**:material-numeric-3-circle:{ .lg .middle }](/blog/knowledge-graph-assignment/mc3/)

    ---

    SPARQL inference system with Wikidata-specific queries:

    * [`wikidata-statement-label.sparql`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/sparqlspace/inference/wikidata-statement-label.sparql)
    * [`wikidata-prop-label.sparql`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/sparqlspace/inference/wikidata-prop-label.sparql)

</div>

In addition, what I feel I got from this course is this:

<div markdown style="text-align: center">
**Use case should drive technology**
</div>

I am reformatting the roadmap for the project with a distinct set of use cases for which Iolanta might be of use, and I am tying enhancements to its technology to those use cases. Primarily, these are the use cases I am interested at myself. Obviously, I will be very happy to find out what other people think.

```mermaid
--8<-- "docs/roadmap/roadmap.mmd"
```

This roadmap demonstrates how technical foundations enable higher-level usecases such as managing ADRs, building roadmaps, and writing nanopublications with Iolanta, reflecting the synthesis of technical and business considerations for real-world knowledge graph applications.

## :material-numeric-3-box: What Still Needs Clarification

* What industries might benefit from an RDF visualization tool?
* What use cases to focus on?
* Are there perspectives of self-sustainability for this project, remembering that it must always remain open source?

## Conclusion

The KGC course helped me shift from building technology in search of problems to identifying usecases that drive technical development. The roadmap reflects this change: technical foundations (facets, SPARQL, inference) now enable specific usecases (nanopublications, ADRs, roadmaps) rather than existing as solutions awaiting applications.

In the purely technological sense,

* I learned a lot about ontology building as a discipline,
* Found out about foundational ontologies,
* Improved my understanding of OWL,
* Got valuable feedback.

Thanks! I greatly enjoyed the experience.
