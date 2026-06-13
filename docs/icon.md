---
"@context": context.yamlld

$id: iolanta:icon
$type: http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
$: icon
iolanta:icon: 🖼️

rdfs:subPropertyOf:
  $id: http://www.wikidata.org/prop/direct/P487
range: xsd:string

comment: |
  Unicode symbol used to compactly represent a resource in Iolanta displays.

hide: [toc]
---

# 🖼️ `iolanta:icon` <small>property</small>

<div class="grid cards annotate" markdown>
-   :material-arrow-up-bold:{ .lg .middle } __Superproperty__

    ---

    [`wdt:P487`](https://www.wikidata.org/wiki/Property:P487)<br/>
    <small>Unicode character</small>

-   :material-target-variant:{ .lg .middle } __Range__

    ---

    [`xsd:string`](/reference/rdfs/literal/)<br/>
    <small>Unicode symbol</small>

</div>

`iolanta:icon` attaches a short Unicode symbol to a resource so Iolanta can use it as a compact visual marker in labels and listings.

```turtle
@prefix iolanta: <https://iolanta.tech/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

rdf:type iolanta:icon "∈" .
```

Use `iolanta:icon` for literal glyphs such as `∈`, `©️`, or `⇔`. For image files, logos, or pictograms stored as media resources, use an image-oriented predicate such as `schema:logo`, `as:icon`, or Wikidata `P2910`.
