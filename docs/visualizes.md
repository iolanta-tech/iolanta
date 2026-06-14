---
"@context": context.yamlld

$id: iolanta:visualizes
iolanta:icon: 👁

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

On the first [`Iolanta.render()`](/reference/iolanta/) call for each `Iolanta` instance, Iolanta queries the public [Knowledge Pixels](https://query.knowledgepixels.com/) nanopub registry for all signed, non-invalidated, non-superseded visualization nanopublications, loads their assertion graphs into the local dataset, and caches the resulting nanopub URL list for one day on disk ([cashews](https://pypi.org/project/cashews/) `@cache.soft` under `~/.cache/iolanta/visualization-index/`). Later renders on the same instance reuse the loaded graphs; nanopub documents are HTTP-cached separately by `yaml-ld` via `requests-cache`. If a registry refresh fails, Iolanta falls back to stale cached URLs when available; otherwise it logs a warning and continues without remote visualizations. Pass `--without-visualization-cache-index` to the CLI to always refresh the URL list from the registry while still updating the disk cache. The grouping triples (`vann:termGroup`, `rdfs:label`) then become visible to the regular ontology-rendering SPARQL used by [`MkDocsOntologyFacet`](/Facet/) and [`OntologyFacet`](/Facet/).

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX np:      <http://www.nanopub.org/nschema#>
PREFIX npx:     <http://purl.org/nanopub/x/>
PREFIX npa:     <http://purl.org/nanopub/admin/>
PREFIX iolanta: <https://iolanta.tech/>

SELECT DISTINCT ?nanopub ?target ?created WHERE {
  GRAPH npa:graph {
    ?nanopub np:hasAssertion ?assertion ;
             np:hasProvenance ?provenance ;
             npa:hasValidSignatureForPublicKey ?pubkey ;
             dcterms:created ?created .
  }

  GRAPH ?provenance {
    ?assertion iolanta:visualizes ?target .
  }

  FILTER NOT EXISTS {
    GRAPH npa:graph {
      ?invalidator npx:invalidates ?nanopub ;
                   npa:hasValidSignatureForPublicKey ?invalidator_pubkey .
    }
  }

  FILTER NOT EXISTS {
    GRAPH npa:graph {
      ?newer npx:supersedes ?nanopub ;
             npa:hasValidSignatureForPublicKey ?newer_pubkey .
    }
  }
}
ORDER BY DESC(?created)
```

Iolanta loads **all** active matches from this index, not only the latest nanopublication per ontology. If multiple signed nanopublications visualize the same ontology, their assertion graphs are all loaded.

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
