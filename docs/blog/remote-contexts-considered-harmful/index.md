---
title: "Remote contexts considered harmful"
description: Remote JSON-LD contexts make document meaning depend on mutable network resources
date: "2026-04-18"
tags: [decision]
hide: [navigation, toc]
"@context":
  - https://json-ld.org/contexts/dollar-convenience.jsonld
  - rdfs: http://www.w3.org/2000/01/rdf-schema#
    skos: http://www.w3.org/2004/02/skos/core#
    qb: http://purl.org/linked-data/cube#
    page: https://iolanta.tech/blog/remote-contexts-considered-harmful/#
    ibis: https://vocab.methodandstructure.com/ibis#
    skos:related:
      "@id": skos:related
      "@type": "@id"
    response:
      "@id": ibis:response
      "@type": "@id"
    supportedBy:
      "@id": ibis:supported-by
      "@type": "@id"
    opposedBy:
      "@id": ibis:opposed-by
      "@type": "@id"
    qb:dataSet:
      "@id": qb:dataSet
      "@type": "@id"
    qb:structure:
      "@id": qb:structure
      "@type": "@id"
    qb:component:
      "@id": qb:component
    qb:dimension:
      "@id": qb:dimension
      "@type": "@id"
    qb:measure:
      "@id": qb:measure
      "@type": "@id"
    qb:order:
      "@id": qb:order
    rdfs:range:
      "@id": rdfs:range
      "@type": "@id"
    alternative:
      "@id": page:alternative
      "@type": "@id"
    riskCriterion:
      "@id": page:riskCriterion
      "@type": "@id"
    mitigationRating:
      "@id": page:mitigationRating
      "@type": "@id"
$included:
  - $type: ibis:Issue
    rdfs:label: How should JSON-LD documents avoid remote context risks?
    rdfs:comment: Remote JSON-LD contexts make document meaning depend on mutable network resources, which creates risks around changed, spoofed, unavailable, privacy-leaking, or overloaded context servers.
    skos:related:
      $id: page:comparison-dataset
      $type: qb:DataSet
      rdfs:label: Comparison of JSON-LD remote context risk mitigations
      qb:structure:
        $type: qb:DataStructureDefinition
        rdfs:label: Comparison matrix structure
        qb:component:
          - qb:dimension:
              $id: page:alternative
              $type: qb:DimensionProperty
              rdfs:label: alternative
              rdfs:range: ibis:Position
            qb:order: 1
          - qb:dimension:
              $id: page:riskCriterion
              $type: qb:DimensionProperty
              rdfs:label: risk criterion
              rdfs:range: skos:Concept
            qb:order: 2
          - qb:measure:
              $id: page:mitigationRating
              $type: qb:MeasureProperty
              rdfs:label: mitigation rating
              rdfs:range: skos:Concept
      $reverse:
        qb:dataSet:
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:context-changed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:context-spoofed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:context-unavailable
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:client-offline
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:privacy-exposure
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:sri
            riskCriterion: page:server-overloaded
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:context-changed
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:context-spoofed
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:context-unavailable
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:client-offline
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:privacy-exposure
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:protected
            riskCriterion: page:server-overloaded
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:context-changed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:context-spoofed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:context-unavailable
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:client-offline
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:privacy-exposure
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:inline-contexts
            riskCriterion: page:server-overloaded
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:context-changed
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:context-spoofed
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:context-unavailable
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:client-offline
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:privacy-exposure
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:hash-fragment
            riskCriterion: page:server-overloaded
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:context-changed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:context-spoofed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:context-unavailable
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:client-offline
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:privacy-exposure
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:content-addressed-context-uris
            riskCriterion: page:server-overloaded
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:context-changed
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:context-spoofed
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:context-unavailable
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:client-offline
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:privacy-exposure
            mitigationRating: page:partially-mitigates
          - $type: qb:Observation
            alternative: page:aggressive-context-caching
            riskCriterion: page:server-overloaded
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:context-changed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:context-spoofed
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:context-unavailable
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:client-offline
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:privacy-exposure
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:vetted-context-allowlist
            riskCriterion: page:server-overloaded
            mitigationRating: page:mitigates
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:context-changed
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:context-spoofed
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:context-unavailable
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:client-offline
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:privacy-exposure
            mitigationRating: page:does-not-mitigate
          - $type: qb:Observation
            alternative: page:origin-policy
            riskCriterion: page:server-overloaded
            mitigationRating: page:does-not-mitigate
    response:
      - $id: page:sri
        $type: ibis:Position
        rdfs:label: JSON-LD @sri
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: Direct analogy to browser SRI
            rdfs:comment: The model is familiar because it mirrors a proven browser standard.
          - $type: ibis:Argument
            rdfs:label: Hash travels with the context reference
            rdfs:comment: The integrity hash is carried by the reference itself, with no separate lockfile.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Structured context references are heavier
            rdfs:comment: A plain context URL becomes an object with metadata, making simple @context usage less readable.
          - $type: ibis:Argument
            rdfs:label: Imported contexts are not covered
            rdfs:comment: The proposal does not yet cover @import chains.
      - $id: page:protected
        $type: ibis:Position
        rdfs:label: JSON-LD @protected
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: Already available in JSON-LD 1.1
            rdfs:comment: Protected terms require no new JSON-LD syntax or future revision.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Meaningful protection requires inline setup
            rdfs:comment: Key terms must be declared inline before loading later contexts, reducing the value of loading them remotely.
          - $type: ibis:Argument
            rdfs:label: Does not authenticate fetched bytes
            rdfs:comment: Protected terms prevent some redefinitions but do not authenticate the remote context or pin its content.
      - $id: page:inline-contexts
        $type: ibis:Position
        rdfs:label: Inline contexts
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: The document carries its own term definitions
            rdfs:comment: Inline contexts make the document fully carry the term definitions it depends on.
          - $type: ibis:Argument
            rdfs:label: Correct processing does not depend on loader policy
            rdfs:comment: Inline contexts avoid depending on cache or document-loader configuration.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Shared contexts are repeated in every document
            rdfs:comment: Large shared contexts such as schema.org become verbose when embedded repeatedly.
          - $type: ibis:Argument
            rdfs:label: Context updates require reissuing documents
            rdfs:comment: Updating an inline context requires reissuing every document that embeds it.
      - $id: page:hash-fragment
        $type: ibis:Position
        rdfs:label: Hash fragment in application/ld+json
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: No author syntax change is required
            rdfs:comment: Hash fragments in HTTP responses are transparent to document authors.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Context servers must cooperate
            rdfs:comment: Existing context servers would need to emit the relevant hash information.
          - $type: ibis:Argument
            rdfs:label: The referencing document does not bind the hash
            rdfs:comment: The hash is supplied by the response server, not by the document that references the context.
      - $id: page:content-addressed-context-uris
        $type: ibis:Position
        rdfs:label: Content-addressed context URIs
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: The URI itself checks integrity
            rdfs:comment: Mutation produces a different content-addressed URI by construction.
          - $type: ibis:Argument
            rdfs:label: Fits Linked Data trust literature
            rdfs:comment: Content-addressed context URIs align with approaches such as Trusty URIs and nanopublications.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Existing context URLs must be replaced or aliased
            rdfs:comment: Location-based context URLs such as schema.org and w3id.org would need a migration path.
          - $type: ibis:Argument
            rdfs:label: Content-addressed context schemes have weak adoption
            rdfs:comment: The ni scheme has no mainstream adoption, and IPFS adds infrastructure dependency.
      - $id: page:aggressive-context-caching
        $type: ibis:Position
        rdfs:label: Aggressively cache contexts
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: Reduces repeated fetches
            rdfs:comment: Caching reduces repeated requests against shared public context servers.
          - $type: ibis:Argument
            rdfs:label: Repeat processing can survive temporary outages
            rdfs:comment: A warm cache can tolerate temporary server or network failures.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: The first fetch is still trusted
            rdfs:comment: Caching does not authenticate the first response or make spoofed bytes trustworthy.
          - $type: ibis:Argument
            rdfs:label: Cached entries may expire or differ by deployment
            rdfs:comment: Cache entries can expire, be evicted, or vary between processors.
      - $id: page:vetted-context-allowlist
        $type: ibis:Position
        rdfs:label: Use a vetted context allowlist
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: Unknown context URLs are refused
            rdfs:comment: A vetted allowlist can refuse unknown context URLs instead of fetching them.
          - $type: ibis:Argument
            rdfs:label: Fits controlled processing environments
            rdfs:comment: A vetted allowlist works well for archival, reproducible, air-gapped, and privacy-sensitive processing.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Vetted copies need an update process
            rdfs:comment: Organizations must update and re-vet cached context copies.
          - $type: ibis:Argument
            rdfs:label: Trust policy does not travel with the document
            rdfs:comment: Another deployment may resolve the same context URLs differently.
      - $id: page:origin-policy
        $type: ibis:Position
        rdfs:label: Origin-based policy
        supportedBy:
          - $type: ibis:Argument
            rdfs:label: No external allowlist is needed
            rdfs:comment: Origin policy can be described without a separate deployment-specific allowlist.
          - $type: ibis:Argument
            rdfs:label: The origin model is widely implemented
            rdfs:comment: Same-origin policy is already implemented by browsers.
        opposedBy:
          - $type: ibis:Argument
            rdfs:label: Shared vocabularies are cross-origin by design
            rdfs:comment: Real JSON-LD documents commonly rely on shared cross-origin vocabularies such as schema.org and w3id.org.
          - $type: ibis:Argument
            rdfs:label: Origin checks do not validate context content
            rdfs:comment: Origin policy restricts who can serve a context, not what bytes the context contains or whether it remains available.
  - $id: page:context-changed
    $type: skos:Concept
    rdfs:label: Context Changed
  - $id: page:context-spoofed
    $type: skos:Concept
    rdfs:label: Context Spoofed
  - $id: page:context-unavailable
    $type: skos:Concept
    rdfs:label: Context Unavailable
  - $id: page:client-offline
    $type: skos:Concept
    rdfs:label: Client Offline
  - $id: page:privacy-exposure
    $type: skos:Concept
    rdfs:label: Privacy Exposure
  - $id: page:server-overloaded
    $type: skos:Concept
    rdfs:label: Server Overloaded
  - $id: page:mitigates
    $type: skos:Concept
    rdfs:label: mitigates
  - $id: page:partially-mitigates
    $type: skos:Concept
    rdfs:label: partially or conditionally mitigates
  - $id: page:does-not-mitigate
    $type: skos:Concept
    rdfs:label: does not mitigate
---

??? note "As a graph"
    ```mermaid
    --8<-- "docs/blog/remote-contexts-considered-harmful/index.mmd"
    ```

# Remote `@context`s considered harmful <small>April 19, 2026</small>

## Problem

A JSON-LD document with a remote context does not fully define its own meaning. Its semantics depend on bytes fetched later from another URL.

The front page of [:material-web: `json-ld.org`](https://json-ld.org/) presents us with an example statement about John Lennon, a famous British rock musician. For the sake of brevity and readability, let's rewrite this example in [YAML-LD](https://www.w3.org/TR/yaml-ld-10/) and render it as a graph.

<div class="grid" markdown>
<div markdown>
```yaml
--8<-- "docs/blog/remote-contexts-considered-harmful/john-lennon.yamlld"
```
</div>
<div markdown>
```mermaid
{{ (docs / 'blog/remote-contexts-considered-harmful/john-lennon.yamlld') | as('mermaid') }}
```
</div>
</div>

The [machine responsible for rendering the graph](https://iolanta.tech) was able to discern that the `born:` property maps to machine-readable [`http://schema.org/birthDate`](http://schema.org/birthDate). That was possible thanks to the remote context that we referenced from [https://json-ld.org/contexts/person.jsonld](https://json-ld.org/contexts/person.jsonld), here is the relevant excerpt:


```json title="person.jsonld"
…
--8<-- "docs/blog/remote-contexts-considered-harmful/person.jsonld:19:23"
…
```

## What could go wrong?

What if the **same** context URL — `https://json-ld.org/contexts/person.jsonld` — returns **different** JSON than authors and readers expect? Nothing in *your* repository needs to change; only the bytes served at that URL change.

For instance, [json-ld.org](https://json-ld.org) has been hacked, and now it returns a hostile response which keeps the same keys yet remaps `born` → `schema:deathDate` and `spouse` → `schema:parent`.

This would alter the meaning of the document about John Lennon:

<div class="grid" markdown>
<div markdown>
```json title="Spoofed person.jsonld (excerpt)"
…
--8<-- "docs/blog/remote-contexts-considered-harmful/person-spoofed.jsonld:16:19"
…
--8<-- "docs/blog/remote-contexts-considered-harmful/person-spoofed.jsonld:59:62"
…
```
</div>
<div markdown>
```mermaid
{{ (docs / 'blog/remote-contexts-considered-harmful/john-lennon-spoofed.yamlld') | as('mermaid') }}
```
</div>
</div>

[JSON-LD 1.1 specification § Security Considerations](https://www.w3.org/TR/json-ld11/#security) warns:

> JSON-LD contexts that are loaded from the Web over non-secure connections, such as
> HTTP, run the risk of being altered by an attacker such that they may modify the
> JSON-LD active context in a way that could compromise security.

Being hacked is not the only risk associated with remote contexts.

## Risks

<div class="grid cards" markdown>

-   :material-pencil:{ .lg .middle } __Context Changed__

    ---

    The context publisher does not need to be malicious for old documents to change meaning. A maintainer can revise a term mapping, publish an incompatible new version at the same URL, or make an ordinary mistake while editing the context. Existing documents keep pointing at the same URL, but now expand to different IRIs than they did when they were written.

-   :material-incognito:{ .lg .middle } __Context Spoofed__

    ---

    The context URL resolves, but returns attacker-controlled content instead of the legitimate context. This can happen through fairly ordinary failures of Internet infrastructure and ownership:

    - [DNS spoofing or cache poisoning](https://www.first.org/global/sigs/dns/stakeholder-advice/detection/cache-poisoning)
    - [Domain name hijacking](https://www.icann.org/en/icann-acronyms-and-terms/domain-name-registration-hijacking-en)
    - [Abandoned infrastructure or expired delegated domains leading to takeover](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover)
    - [Cybersquatting](https://www.wipo.int/pressroom/en/prdocs/1999/wipo_pr_1999_170.html)

    ActivityPub implementations resolve JSON-LD over the wire when handling remote actors and objects; that has produced both shipped vulnerabilities and long-running design discussion about attacker-controlled contexts:

    - [:material-github: mastodon/mastodon GHSA-3fjr-858r-92rw](https://github.com/mastodon/mastodon/security/advisories/GHSA-3fjr-858r-92rw)
    - [SocialHub — remote JSON-LD contexts in federation](https://socialhub.activitypub.rocks/t/potential-security-vulnerability-remote-json-ld-contexts-may-be-used-to-bypass-restrictions-when-arbitrary-objects-are-allowed-to-be-created/5439)

-   :material-link-off:{ .lg .middle } __Context Unavailable__

    ---

    The context URL stops resolving entirely. A processor that cannot retrieve a context cannot expand any of the terms it defines, so the document becomes unprocessable regardless of whether its own bytes are intact. Remote URLs are inherently fragile over time: link rot, server shutdowns, and deleted documents are ordinary events on a long enough horizon.

-   :material-lan-disconnect:{ .lg .middle } __Client Offline__

    ---

    Many JSON-LD and YAML-LD workflows need documents to remain processable without any network access at all: air-gapped deployments, archival workflows, reproducible builds, local analysis, privacy-sensitive processing, or simply working offline on a laptop. This is separate from server failure: a context server may be healthy and reachable in principle, yet the document still fails in any environment that forbids or lacks network access.

-   :material-eye-outline:{ .lg .middle } __Privacy Exposure__

    ---

    Each remote context fetch tells the context publisher *which document* is being processed and *by whom* — a timing and correlation signal. The JSON-LD WG addresses this under privacy considerations for remote contexts ([:material-github: w3c/json-ld-syntax#430](https://github.com/w3c/json-ld-syntax/issues/430)).

-   :material-server-network:{ .lg .middle } __Server Overloaded__

    ---

    A context URL shared across millions of documents generates a fetch every time any processor encounters any of those documents. High-volume deployments such as ActivityPub federation, Verifiable Credential issuers, and bulk RDF pipelines can produce enormous request rates against a handful of context servers. This is precisely why the JSON-LD Best Practices [recommend liberal cache-control headers](https://w3c.github.io/json-ld-bp/#cache) and why implementations such as [:material-github: mastodon/mastodon#9412](https://github.com/mastodon/mastodon/pull/9412) cache contexts rather than fetching them on demand.

</div>

The specification itself points toward one mitigation direction for semantic instability, which brings us to the first alternative.

## Alternatives

The matrix below summarizes how each alternative addresses the six risks above. Each alternative name links to its tab for details.

Legend: :white_check_mark: mitigates, :warning: partially or conditionally mitigates, :x: does not mitigate.

|  | Context Changed | Context Spoofed | Context Unavailable | Client Offline | Privacy Exposure | Server Overloaded |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| [`@sri`](#sri) | :white_check_mark: | :white_check_mark: | :x: | :x: | :warning: | :warning: |
| [`@protected`](#protected) | :warning: | :warning: | :x: | :x: | :x: | :x: |
| [Inline Contexts](#inline) | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Hash Fragment in `application/ld+json`](#hash) | :x: | :x: | :x: | :x: | :x: | :x: |
| [Content-Addressed Context URIs](#content-addressed) | :white_check_mark: | :white_check_mark: | :warning: | :warning: | :warning: | :warning: |
| [Aggressively Cache Contexts](#cache) | :warning: | :warning: | :warning: | :warning: | :warning: | :white_check_mark: |
| [Use a Vetted Context Allowlist](#allowlist) | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Origin-Based Policy](#origin) | :x: | :x: | :x: | :x: | :x: | :x: |

The tabs below provide the example and the implementation tradeoffs for each alternative.

=== "`@sri`"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.sri.md"

=== "`@protected`"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.protected.md"

=== "Inline"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.inline-contexts.md"

=== "Hash"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.hash-fragment.md"

=== "Content-Addressed"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.content-addressed.md"

=== "Cache"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.aggressive-caching.md"

=== "Allowlist"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.vetted-context-allowlist.md"

=== "Origin"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.origin-policy.md"
