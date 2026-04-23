---
title: "Remote contexts considered harmful"
description: Remote JSON-LD contexts make document meaning depend on mutable network resources
date: "2026-04-18"
tags: [decision]
hide: [navigation, toc]
---

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

For instance, (json-ld.org)[https://json-ld.org] has been hacked, and now it returns a hostile response which keeps the same keys yet remaps `born` → `schema:deathDate` and `spouse` → `schema:parent`.

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

    A context URL shared across millions of documents generates a fetch every time any processor encounters any of those documents. High-volume deployments such as ActivityPub federation, Verifiable Credential issuers, and bulk RDF pipelines can produce enormous request rates against a handful of context servers. This is precisely why the JSON-LD Best Practices [recommend liberal cache-control headers](https://w3c.github.io/json-ld-bp/#cache) and why implementations such as [:material-github: mastodon/mastodon#9412](https://github.com/mastodon/mastodon/pull/9412) rather than fetching them on demand.

</div>

The specification itself points toward one mitigation direction for semantic instability, which brings us to the first alternative.

## Alternatives

The matrix below summarizes how each alternative addresses the six risks above. Each alternative name links to its tab for details.

Legend: :white_check_mark: mitigates, :warning: partially or conditionally mitigates, :x: does not mitigate.

|  | Context Changed | Context Spoofed | Context Unavailable | Client Offline | Privacy Exposure | Server Overloaded |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| [`@sri`](#sri) | :white_check_mark: | :white_check_mark: | :x: | :x: | :warning: | :warning: |
| [`@protected`](#protected) | :warning: | :warning: | :x: | :x: | :x: | :x: |
| [Inline Contexts](#inline-contexts) | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Hash Fragment in `application/ld+json`](#hash-fragment-in-applicationldjson) | :x: | :x: | :x: | :x: | :x: | :x: |
| [Content-Addressed Context URIs](#content-addressed-context-uris) | :white_check_mark: | :white_check_mark: | :warning: | :warning: | :warning: | :warning: |
| [Permanently Cache Vetted Contexts](#permanently-cache-vetted-contexts) | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| [Origin-Based Policy](#origin-based-policy) | :x: | :x: | :x: | :x: | :x: | :x: |

The tabs below provide the example and the implementation tradeoffs for each alternative.

=== "`@sri`"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.sri.md"

=== "`@protected`"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.protected.md"

=== "Inline Contexts"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.inline-contexts.md"

=== "Hash Fragment in `application/ld+json`"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.hash-fragment.md"

=== "Content-Addressed Context URIs"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.content-addressed.md"

=== "Permanently Cache Vetted Contexts"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.cached-contexts.md"

=== "Origin-Based Policy"

    --8<-- "docs/blog/remote-contexts-considered-harmful/.origin-policy.md"
