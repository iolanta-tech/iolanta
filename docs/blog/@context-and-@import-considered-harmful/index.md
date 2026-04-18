---
title: "`@context` & `@import` considered harmful"
description: Remote JSON-LD contexts create trust, integrity, and availability problems
date: "2026-04-18"
tags: [decision]
hide: [navigation]
---

# `@context` & `@import` considered harmful <small>April 18, 2026</small>

## A concrete example

Start with the official JSON-LD site example, rewritten in YAML-LD for readability.
The vulnerability is the same in JSON-LD and YAML-LD because they use the same
JSON-LD data model and the same remote-context loading rules.

```yaml
--8<-- "docs/blog/@context-and-@import-considered-harmful/john-lennon.yamlld"
```

The meaning of that document depends on what the remote context returns. At the time
of writing, the relevant part of `https://json-ld.org/contexts/person.jsonld` is:

```json
--8<-- "docs/blog/@context-and-@import-considered-harmful/person-context-excerpt.jsonld"
```

Interpreted with that context, the document means:

```mermaid
{{ (docs / 'blog/@context-and-@import-considered-harmful/john-lennon.yamlld') | as('mermaid') }}
```

## Problem

The [JSON-LD 1.1 specification § Security Considerations](https://www.w3.org/TR/json-ld11/#security) warns:

> JSON-LD contexts that are loaded from the Web over non-secure connections, such as
> HTTP, run the risk of being altered by an attacker such that they may modify the
> JSON-LD active context in a way that could compromise security.

The John Lennon example above already shows the problem. The YAML-LD document is
short and harmless-looking, but its meaning depends entirely on whoever answers
`https://json-ld.org/contexts/person.jsonld`. If that server returns a modified
context where `spouse` maps to `schema:parent`, or `born` maps to
`schema:deathDate`, the rendered graph changes even though the document bytes do not.

This becomes dangerous in signed or otherwise security-sensitive systems: the document
can keep the same shape while its semantics move underneath it. Signatures protect the
*canonicalized RDF triples*, not the `@context` URL or its contents.

As of 2026, the older PaySwarm context `http://purl.org/payswarm/v1` no longer
resolves at all: the domain is unreachable. This is not an attack — it is ordinary
link rot — but the effect on dependent documents is identical: the context is gone,
and with it the meaning of every document that referenced it.

### From specification example to real-world exploit

The PaySwarm scenario is not hypothetical. Mastodon has had documented incidents
where ActivityPub objects with attacker-controlled `@context` URLs were used for
remote actor impersonation. A poisoned context redefined terms in ways that bypassed
access restrictions — a direct instantiation of the attack the spec describes:

- [Mastodon GHSA-3fjr-858r-92rw](https://github.com/mastodon/mastodon/security/advisories/GHSA-3fjr-858r-92rw)
- [ActivityPub context vulnerability discussion](https://socialhub.activitypub.rocks/t/potential-security-vulnerability-remote-json-ld-contexts-may-be-used-to-bypass-restrictions-when-arbitrary-objects-are-allowed-to-be-created/5439)

### The problem

This class of vulnerability is sometimes called *context switching*: the attacker
replaces the context a document was authored with, changing the meaning of its terms
without invalidating any proof. It arises from a structural property of JSON-LD
processing: `@context` (and `@import`) are fetched and applied *before* any
cryptographic verification, and they are not included in the signature scope.

Two further variants make the problem broader:

**`@vocab` / `@base` override.** The `@protected` keyword guards individual term
definitions but not terms resolved through `@vocab` or `@base`. A replacement context
can redefine the entire default namespace without triggering any protection
([w3c/vc-data-integrity#272](https://github.com/w3c/vc-data-integrity/issues/272)).

**The `@import` gap.** `@import` (JSON-LD 1.1) has zero integrity protection in any
existing specification — not covered by `@protected`, `digestMultibase`, or any
proposed `@sri` mechanism.

### Alternatives

#### Inline contexts

Instead of a URL reference, embed the full context JSON directly in the document.

```json
{
  "@context": {
    "salary": "https://example.org/salary",
    "employer": "https://example.org/employer"
  }
}
```

- **Pro:** No remote fetch; content is cryptographically bound to the document
- **Pro:** No dependency on network availability or server longevity
- **Con:** Verbose; large shared contexts (schema.org) repeated in every document
- **Con:** No deduplication; context updates require re-issuing all documents

---

#### `@sri` inline ([w3c/json-ld-syntax#108](https://github.com/w3c/json-ld-syntax/issues/108))

The JSON-LD 1.1 specification notes that future versions may incorporate
[Subresource Integrity](https://www.w3.org/TR/SRI/) as a mitigation
([w3c/json-ld-syntax#86](https://github.com/w3c/json-ld-syntax/issues/86)), but this
has not yet happened in JSON-LD 1.1. A concrete syntax proposal is the `@sri`
keyword alongside a context reference, mirroring HTML SRI:

```json
{
  "@context": {
    "@value": "https://schema.org/",
    "@sri": "sha256-abc123..."
  }
}
```

- **Pro:** Direct analogy to a proven browser standard (HTML SRI)
- **Pro:** Hash travels with the reference; no separate lockfile
- **Con:** Deferred to a future JSON-LD version; no specification text yet
- **Con:** Syntax ambiguity: how to distinguish metadata objects from inline
  context-by-value objects
- **Con:** Does not yet cover `@import` chains
- **Con:** Does not address the unsigned-`@context`-in-signed-documents flaw — the
  `@sri` value itself is still outside proof scope

---

#### Context pinning lockfile ([w3c/json-ld-syntax#422](https://github.com/w3c/json-ld-syntax/issues/422))

A separate file mapping context URLs to expected hashes, analogous to npm's
`package-lock.json` or pip's `--require-hashes`:

```yaml
# context-lock.yaml
"https://schema.org/":
  sha256: abc123...
"https://w3id.org/security/v1":
  sha256: def456...
```

- **Pro:** No change to JSON-LD syntax; works with any existing processor via a
  custom document loader
- **Pro:** Proven pattern in other ecosystems (npm, pip, Cargo)
- **Pro:** Tooling can auto-generate and update the lockfile
- **Con:** Out-of-band; the lockfile must be distributed alongside documents
- **Con:** No standard; each implementation invents its own format
- **Con:** Still does not bind the context hash into proof scope

---

#### `digestMultibase` on context resources ([VC Data Integrity 1.0](https://www.w3.org/TR/vc-data-integrity/))

The existing `digestMultibase` mechanism attaches a hash to any resource with an `id`:

```json
{
  "image": {
    "id": "https://example.org/photo.jpg",
    "digestMultibase": "zQmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n"
  }
}
```

- **Pro:** Already a W3C Recommendation; implemented in some VC libraries
- **Con:** `@context` string references have no `id` property — the mechanism cannot
  be applied to context URLs at all
- **Con:** Even where applicable, the hash is document data, not part of the proof

---

#### Hash fragment in `application/ld+json` media type ([JSON-LD WG charter 2025–2028](https://w3c.github.io/json-ld-charter-2025/))

The JSON-LD WG intends to add a content hash to HTTP responses serving JSON-LD
contexts, allowing processors to verify what they receive:

```
Content-Type: application/ld+json; hash="sha256-abc123..."
```

- **Pro:** Enforcement at the transport layer, analogous to how SRI works in browsers
- **Pro:** Transparent to document authors; no syntax change required
- **Con:** Still exploratory; no draft specification
- **Con:** Requires server-side adoption; existing context servers (schema.org,
  w3id.org) would need to emit the header
- **Con:** Does not help for contexts already cached or served by third parties

---

#### Include `@context` hash in proof scope ([w3c/vc-data-integrity#272](https://github.com/w3c/vc-data-integrity/issues/272))

Redesign Data Integrity proofs to cryptographically bind the context to the signature:

```json
{
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "proofValue": "...",
    "contextDigest": "sha256-abc123..."
  }
}
```

- **Pro:** Closes the architectural flaw completely; context mutation invalidates the
  proof
- **Pro:** No separate lockfile or transport mechanism needed
- **Con:** Backwards-incompatible; all existing signed documents would fail verification
- **Con:** Requires consensus in VC WG and JSON-LD WG; no specification text yet
- **Con:** Complicates context chains: what is hashed when multiple `@context` entries
  merge with `@import` chains?

---

#### Content-addressed context URIs

Replace location-based context URLs with content-hash-based URIs (IPFS CIDs, `ni:`
URIs per [RFC 6920](https://datatracker.ietf.org/doc/html/rfc6920), or Trusty URIs):

```
ni:///sha-256;abc123...?ct=application/ld+json
```

- **Pro:** The URI *is* the integrity check; mutation produces a different URI by
  construction
- **Pro:** Consistent with the broader Linked Data trust literature (Trusty URIs,
  nanopublications)
- **Con:** Requires minting new URIs; all existing context URLs (schema.org, w3id.org)
  would need to be replaced or aliased
- **Con:** `ni:` scheme has no mainstream adoption; IPFS adds infrastructure dependency
- **Con:** Context versioning becomes explicit URI changes, which may complicate
  backwards compatibility

---

#### Permanently cache vetted contexts (operational mitigation)

Rather than a protocol fix, organizations vet and locally cache a known-good snapshot
of each context, blocking all remote fetches in production:

```python
document_loader = StaticDocumentLoader({
    "https://schema.org/": open("cache/schema.org.jsonld").read(),
})
```

- **Pro:** Implementable today with any JSON-LD processor via a custom document loader
- **Pro:** Eliminates TOCTOU window entirely for cached contexts
- **Con:** Requires an organizational process to update and re-vet cached copies
- **Con:** Not a standard; each team implements independently
- **Con:** Context updates are silent unless the vetting process catches them

#### Origin-based policy ([RFC 6454](https://www.rfc-editor.org/rfc/rfc6454.html))

[RFC 6454](https://www.rfc-editor.org/rfc/rfc6454.html) defines the *Web Origin
Concept*: an origin is the triple of scheme, host, and port computed from a URL.
Browsers use it to enforce the same-origin policy — a document from origin A may
only access resources from origin A by default; cross-origin access requires explicit
server permission (CORS).

Applied to JSON-LD context loading: a document from `https://example.org` would only
be permitted to load contexts from `https://example.org`. For cross-origin contexts,
RFC 6454 defines the `Origin` request header to declare the requester's origin; the
context server responds with `Access-Control-Allow-Origin` (CORS) to grant or deny
access. JSON-LD processors do not currently enforce this — they fetch contexts without
checking CORS headers — but the mechanism exists at the HTTP level and could be applied.

- **Pro:** Policy is self-describing; no external configuration or allowlist needed
- **Pro:** Well-established model already implemented in every web browser
- **Con:** Most real JSON-LD usage is cross-origin by design — schema.org, w3id.org,
  and similar shared vocabularies would be blocked by default, making this policy
  impractical without a cross-origin permission mechanism
- **Con:** Restricts *who* can serve contexts, not *what* they contain; a same-origin
  server can still change or lose its context
- **Con:** Does not address link rot or content integrity

---

## Decision

*(To be completed.)*

## Consequences

*(To be completed.)*

---

## References

- [JSON-LD WG Charter 2025](https://w3c.github.io/json-ld-charter-2025/)
- [Verifiable Credential Data Integrity 1.0](https://www.w3.org/TR/vc-data-integrity/)
- [w3c/json-ld-syntax#108 — `@sri` proposal](https://github.com/w3c/json-ld-syntax/issues/108)
- [w3c/json-ld-syntax#422 — context pinning](https://github.com/w3c/json-ld-syntax/issues/422)
- [w3c/json-ld-syntax#430 — privacy considerations for remote contexts](https://github.com/w3c/json-ld-syntax/issues/430)
- [w3c/json-ld-syntax#443 — `@protected` conflicts](https://github.com/w3c/json-ld-syntax/issues/443)
- [w3c/vc-data-integrity#272 — unsigned `@context` in signed documents](https://github.com/w3c/vc-data-integrity/issues/272)
- [Mastodon GHSA-3fjr-858r-92rw](https://github.com/mastodon/mastodon/security/advisories/GHSA-3fjr-858r-92rw)
- [ActivityPub context vulnerability discussion](https://socialhub.activitypub.rocks/t/potential-security-vulnerability-remote-json-ld-contexts-may-be-used-to-bypass-restrictions-when-arbitrary-objects-are-allowed-to-be-created/5439)
- [MDN: Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)
- [RFC 6920 — Naming Things with Hashes](https://datatracker.ietf.org/doc/html/rfc6920)
- [Artz & Gil (2007) — A Survey of Trust in Computer Science and the Semantic Web](https://www.sciencedirect.com/science/article/abs/pii/S1570826807000133)
