---
date: "2025-03-30"
hide:
  - toc
---

# Use `dcterms:isReferencedBy` to let Iolanta know where to fetch information about a thing

## Why

Sometimes, a URI that describes something is, by itself, not resolvable. For instance, **W3C License** is specified by

```
https://purl.org/NET/rdflicense/W3C1.0
```

but resolving this URL won't return anything. In this case, you can use `dcterms:isReferencedBy` to point to a document that describes the thing.

## How

```yaml
"@context":
  "@import": https://json-ld.org/contexts/dollar-convenience.jsonld
  dcterms: http://purl.org/dc/terms/

  dcterms:isReferencedBy:
    "@type": "@id"

$id: https://purl.org/NET/rdflicense/W3C1.0
dcterms:isReferencedBy: https://purl.org/NET/rdflicense/W3C1.0.ttl
```

Whenever Iolanta encounters the URI of W3C 1.0 license it will retrieve the specified Turtle document which provides information about it.
