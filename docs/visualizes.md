---
hide: [toc]
---

# :material-eye-check-outline: `iolanta:visualizes` <small>property</small>

<div class="grid cards" markdown>
-   :material-arrow-expand-right:{ .lg .middle } __Domain__

    ---

    `np:Assertion`<br/>
    <small>An assertion graph inside a nanopublication</small>

-   :material-target-variant:{ .lg .middle } __Range__

    ---

    [`owl:Ontology`](https://www.w3.org/TR/owl2-syntax/#Ontologies)<br/>
    <small>The ontology this assertion describes how to render</small>

</div>

`iolanta:visualizes` links a [nanopublication](/blog/2025-01-21-nanopublications/) assertion to the ontology whose visualization metadata it carries. The triple lives in the nanopublication's [provenance graph](https://nanopub.net/), not its assertion graph: the *assertion* describes how to group an ontology's terms (using `vann:termGroup`), while the *provenance* says which ontology that assertion is about.

Iolanta uses `iolanta:visualizes` at render time to discover community-published visualization information for any ontology, without that information having to be bundled in the Iolanta repository. See the related ADR: [Publish visualization information for ontologies on …](/blog/publish-visualization-information-for-ontologies-on/).

## Discovery flow

When [`MkDocsOntologyFacet`](/Facet/) or [`OntologyFacet`](/Facet/) is asked to render an ontology `<O>`, it queries the public [Knowledge Pixels](https://query.knowledgepixels.com/) nanopub registry for the most recent signed, non-invalidated, non-superseded nanopublication whose provenance asserts `?assertion iolanta:visualizes <O>`, and loads that nanopublication's assertion graph into the local dataset. The grouping triples (`vann:termGroup`, `rdfs:label`) then become visible to the regular ontology-rendering SPARQL.

```sparql
SELECT ?nanopub WHERE {
  ?nanopub np:hasAssertion       ?assertion ;
           np:hasProvenance      ?provenance ;
           np:hasPublicationInfo ?pubinfo ;
           npa:hasValidSignatureForPublicKey ?pubkey .

  GRAPH ?provenance { ?assertion iolanta:visualizes <O> }
  GRAPH ?pubinfo    { ?nanopub  dcterms:created     ?created }

  FILTER NOT EXISTS {
    ?invalidator npx:invalidates ?nanopub ;
                 npa:hasValidSignatureForPublicKey ?invalidator_pubkey .
  }
  FILTER NOT EXISTS {
    ?newer npx:supersedes ?nanopub ;
           npa:hasValidSignatureForPublicKey ?newer_pubkey .
  }
}
ORDER BY DESC(?created)
LIMIT 1
```

`ORDER BY DESC(?created) LIMIT 1` is **last-writer-wins**: only one nanopublication per ontology is loaded so different publishers' grouping schemes never mix. To override what Iolanta picks up for a given ontology, sign and publish a newer nanopublication.

The discovery code lives in [`iolanta/discovery/visualization_nanopublications.py`](https://github.com/iolanta-tech/iolanta/blob/master/iolanta/discovery/visualization_nanopublications.py).

## Example

The current grouping for the [`rdf:` namespace](/reference/rdf/) is loaded from [`https://w3id.org/np/RAXhiZMoa3JldEhxcgVyp8UIJL_N0PhEJpCTRXdKl7H_Q`](https://w3id.org/np/RAXhiZMoa3JldEhxcgVyp8UIJL_N0PhEJpCTRXdKl7H_Q). Its provenance graph contains, in essence:

```yaml
"@context":
  iolanta: https://iolanta.tech/
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#

$id: "_:assertion"
iolanta:visualizes:
  $id: "rdf:"
```

…and its assertion graph contains the `vann:termGroup` triples that produce the *Datatype / Language / Triples / Compound Literal / Containers / Properties / Value* groups visible on the [RDF reference page](/reference/rdf/).
