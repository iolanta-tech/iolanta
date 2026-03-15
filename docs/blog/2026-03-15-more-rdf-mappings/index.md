---
title: The more RDF mappings, the better
description: It makes sense to map RDF to multiple data formats
date: "2026-03-15"
hide: [navigation, toc]
---

# The more RDF mappings, the better <small>March 15, 2026</small>

> **6.5** For an answer which cannot be expressed the question too cannot be expressed.
>
> — **Ludwig Wittgenstein** [Tractatus Logico-Philosophicus](https://en.wikisource.org/wiki/Tractatus_Logico-Philosophicus/6#6.5)

## Motivation

From time to time, I encounter discussions about which data formats are better to map to RDF:

- [TOML](https://toml.io/) vs YAML?
- [BSON](https://bsonspec.org/) vs CBOR?
- …and so on

This post argues that such discussions may not be entirely productive.

## RDF

**RDF *(Resource Description Framework)*** is a very simple data model. Indeed, [RDF 1.1](https://www.w3.org/TR/rdf11-concepts/) introduces very few notions — a node, a property, URI, Blank Node, and Literal. Datatype is not required for understanding; Named Graph and Dataset are a bonus. With this toolset, RDF aims to convey knowledge about this Multiverse.

RDF is not a silver bullet — it cannot be the best data model for every use case. Arguably, RDF can be described as a *lingua franca* — the intermediary model which facilitates communication among people and machines even if they speak many different data models, formats, and languages.

To that end, there are *mappings* of RDF to various data formats, through which it becomes straightforward to convey RDF semantics using native languages of systems which do not necessarily speak RDF.

Here is a small RDF graph in :material-turtle: [Turtle](https://www.w3.org/TR/turtle/):

<div class="grid" markdown>
<div markdown>
```turtle
--8<-- "docs/blog/2026-03-15-more-rdf-mappings/example.ttl"
```
</div>
<div markdown>
!!! success "Pro"
    - Well-suited for authoring RDF by hand or with an LLM
    - Comments supported
    - Widely supported across RDF tooling
    - Concise, reduces repetition in objects and properties

!!! failure "Contra"
    - Less familiar to developers outside the RDF community
</div>
</div>

The graph looks like this:

```mermaid
{{ (docs / 'blog/2026-03-15-more-rdf-mappings/example.ttl') | as('mermaid') }}
```

Turtle is the default format of examples in RDF specifications, but it is not the only one.

## [JSON-LD](https://www.w3.org/TR/json-ld11/) <small>based on [:simple-json: JSON](https://www.json.org/)</small>

JSON-LD is useful when a system already speaks JSON and you want [Linked Data](https://www.w3.org/wiki/LinkedData) semantics without leaving that ecosystem.

<div class="grid" markdown>
<div markdown>
```json
--8<-- "docs/blog/2026-03-15-more-rdf-mappings/example.jsonld"
```
</div>
<div markdown>
!!! success "Pro"
    - Native to web browsers and APIs; embeddable in `<script>` tags
    - Widely supported by search engines for structured data
    - JSON supported by every language & ecosystem

!!! failure "Contra"
    - Comments not supported
    - Harder to write by hand or with an LLM
</div>
</div>

## [YAML-LD](https://w3c.github.io/yaml-ld/) <small>based on [:simple-yaml: YAML](https://yaml.org/)</small>

YAML-LD is useful when the same semantics should be carried in a format that is friendlier for manual authoring and configuration-oriented workflows.

<div class="grid" markdown>
<div markdown>
```yaml
--8<-- "docs/blog/2026-03-15-more-rdf-mappings/example.yamlld"
```
</div>
<div markdown>
!!! success "Pro"
    - Supports the full JSON-LD data model
    - Well-suited for authoring RDF by hand or with an LLM
    - Supports comments
    - YAML supported by every language & ecosystem

!!! failure "Contra"
    - YAML 1.1 has implicit type coercions that surprise developers, such as the [Norway problem](https://www.bram.us/2022/01/11/yaml-the-norway-problem/)
        - Fixed by YAML 1.2
</div>
</div>

## [RDF/XML](https://www.w3.org/TR/rdf-syntax-grammar/) <small>based on [:material-xml: XML](https://www.w3.org/XML/)</small>

RDF/XML remains useful wherever XML tooling, storage, or institutional constraints are already present.

<div class="grid" markdown>
<div markdown>
```xml
--8<-- "docs/blog/2026-03-15-more-rdf-mappings/example.rdf"
```
</div>
<div markdown>
!!! success "Pro"
    - Over two decades of institutional adoption and tooling
    - [XSLT](https://www.w3.org/TR/xslt-30/), [XQuery](https://www.w3.org/TR/xquery-31/), [XPath](https://www.w3.org/TR/xpath-31/) and other XML-specific tools available

!!! failure "Contra"
    - Notoriously hard to read and write by hand or LLM
    - Multiple valid serialisations of the same graph make diffing hard
</div>
</div>

## [CBOR-LD](https://w3c.github.io/cbor-ld/) <small>based on [:fontawesome-solid-square-binary: CBOR](https://cbor.io/)</small>

CBOR-LD is a binary format useful when bandwidth or storage is the constraint.

<div class="grid" markdown>
<div markdown>
{{ colored_bytes(docs / 'blog/2026-03-15-more-rdf-mappings/example.cborld') }}
406 bytes — 36% smaller than JSON-LD, using the [reference JS implementation](https://github.com/digitalbazaar/cborld). With a registered context, compression would exceed 60%.
</div>
<div markdown>
!!! success "Pro"
    - Dramatically smaller than any text format — fits RDF into QR codes, barcodes, and constrained devices
    - Builds on the JSON-LD ecosystem: any JSON-LD document can be encoded
    - Payload is self-describing via the `0xcb1d` CBOR tag; no out-of-band schema needed

!!! failure "Contra"
    - Binary — not human-readable or diffable
    - Full semantic compression requires contexts registered in the [CBOR-LD registry](https://json-ld.github.io/cborld-registry/)
</div>
</div>

## The point

RDF mappings do not compete with each other — they extend the reach of RDF as a *lingua franca*. Ideally, for every widely-used data format, a well-specified RDF mapping should exist.

The [JSON-LD Working Group](https://www.w3.org/groups/wg/json-ld/) is working on making that happen. You are welcome to join.
