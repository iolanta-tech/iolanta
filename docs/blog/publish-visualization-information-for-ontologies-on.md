---
title: Publish visualization information for ontologies on …
status: decided
date: "2026-05-06"
tags: [decision]
hide: [navigation]
---

# Publish visualization information for ontologies on …

## Context

Iolanta currently has a visualization index YAML-LD file, but that index is centralized, wired into the codebase, and not usable by other publishers. Ontology publishers should be able to publish accompanying visualization information for an ontology, such as multilingual labels and VANN term groups, so Iolanta can discover and use it. The immediate target is ontology visualization data such as IBIS, while the mechanism should leave room for other resource types later.

The solution needs to:

- Let a third-party ontology publisher publish visualization data without changing Iolanta's source tree.
- Let Iolanta discover visualization data starting from the ontology IRI or from data already found while dereferencing it.
- Support visualization data for ontologies Iolanta does not control and cannot ask to change, including RDF, RDFS, OWL, and other canonical vocabularies.
- Keep visualization data in RDF or Linked Data so existing SPARQL loading and facet selection can consume it.
- Support multiple complementary sources, because authoritative publisher data, community annotations, immutable snapshots, and local fallbacks may coexist.
- Preserve the current expressivity of visualization overlays, including `rdfs:label` values with language tags and `vann:termGroup` group definitions.
- Work for ontologies first without baking ontology-specific assumptions into the discovery layer.
- Make discovery inspectable and debuggable, so Iolanta can report which visualization sources were found, loaded, skipped, or rejected.
- Avoid treating third-party descriptions as authoritative merely because they are discoverable.

## Decision

Use nanopublications as the primary public publication and discovery mechanism for third-party visualization information, with publisher-controlled links as an optimization when the ontology publisher cooperates, and Iolanta packages or plugins as local fallback. A visualization nanopublication should identify the ontology it describes and contain or reference RDF visualization data that Iolanta can load; the same reverse-description triple can also appear in catalog records, package metadata, or publisher-controlled visualization documents.

| Status | Item | Discovery | Description |
|--------|------|-----------|-------------|
| ✅ | [Nanopublications](https://nanopub.net/docs/architecture/) | ✅ Public query/discovery network | Publish visualization assertions as provenance-carrying RDF publications that can be queried and cited independently of the ontology host. This covers RDF, RDFS, OWL, and other vocabularies whose canonical documents Iolanta cannot change. |
| ✅ | Iolanta package or plugin metadata | ✅ Local installed discovery | Let installable Iolanta extensions ship visualization overlays for vocabularies they support, and keep bundled overlays as an offline fallback. |
| ✅ | Publisher-controlled ontology RDF links to visualization RDF | ⚠️ Only from cooperative ontology documents | Accept as an optional discovery input when the ontology publisher controls the ontology document. This cannot cover RDF, RDFS, OWL, or other vocabularies whose canonical documents Iolanta cannot change, so it cannot be the primary mechanism. |
| ✅ | Publisher-controlled HTTP `Link` headers with `describedby` | ⚠️ Only from cooperative ontology origins | Accept as an optional discovery input when the ontology publisher controls the HTTP response and can advertise visualization metadata with the [`describedby`](https://www.iana.org/assignments/link-relations) relation. This cannot cover vocabularies whose origin Iolanta does not control. |
| ❌ | [DCAT](https://www.w3.org/TR/vocab-dcat/) or [VoID](https://www.w3.org/2001/sw/interest/void/) catalog as a selected mechanism | ⚠️ Needs catalog discovery | Useful as metadata inside or around nanopublications, but not sufficient as a selected mechanism without also choosing which catalog Iolanta should query. |
| ❌ | [Web Annotation](https://www.w3.org/TR/annotation-model/) as a selected mechanism | ⚠️ Needs annotation index discovery | Useful as a modeling pattern, but not sufficient as a selected mechanism without also choosing which annotation index Iolanta should query. |
| ❌ | [IPFS](https://docs.ipfs.tech/how-to/content-addressing-data-sets/) or IPLD as a selected mechanism | ❌ No discovery by itself | Useful for immutable visualization snapshots referenced from nanopublications, catalogs, publisher links, or plugin metadata, but content addressing does not solve discovery by itself. |
| ❌ | Well-known visualization index on the ontology origin | ❌ No discovery for uncontrolled origins | Define an Iolanta-specific [well-known URI](https://www.rfc-editor.org/rfc/rfc8615.html), but this still requires control over the ontology origin, so it does not work for RDF, RDFS, OWL, or other canonical vocabularies Iolanta cannot ask to change. |
| ❌ | [LDP](https://www.w3.org/TR/ldp/) or [Solid Type Index](https://solid.github.io/type-indexes/) registry | ⚠️ Needs registry discovery | This gives an enumerable container, but Iolanta would still need to know which registry to ask, and it adds a server or account model that is heavier than publishing nanopublications. |
| ❌ | Built-in centralized Iolanta visualization index as the primary mechanism | ✅ Iolanta-controlled discovery only | This is the current implementation, but it requires Iolanta source changes and does not let other publishers participate directly. |

Each selected publication mechanism must include RDF that links the visualization data back to the ontology it describes, so Iolanta can query by ontology IRI after the publication mechanism has exposed or indexed the RDF.

## Consequences

- Iolanta will need a discovery layer that can gather visualization candidates from more than one mechanism and load all accepted RDF graphs.
- The current bundled visualization index can remain as a compatibility fallback, but not as the only publication path.
- Discovery and trust policy need to be separate: finding a visualization graph does not imply that Iolanta should prefer it over publisher-controlled, user-configured, or locally installed data.

#### Implementation Steps

- [ ] Define the minimum RDF shape for a visualization document that describes an ontology.
- [ ] Replace the hardcoded visualization index load with a visualization discovery service.
- [ ] Teach the ontology facet to use discovered visualization graphs before rendering term groups and labels.
- [ ] Keep the bundled index as a fallback source while external publication mechanisms are introduced.
- [ ] Add regression tests using IBIS-like ontology data and an externally published visualization graph.
