---
"@context": ../context.yamlld

$id: https://iolanta.tech/datatypes/jsonl
$type: iolanta:OutputDatatype
$: JSON Lines
hide: toc

⊆: xsd:string

rdfs:comment: >
  [JSON Lines](https://jsonlines.org/) (newline-delimited JSON) output format.
  One JSON object per line, terminated by `\n`. Suitable for streaming
  pipelines: each line is independently parseable, and consumers can process
  output incrementally (e.g. piping through `jq -c .`).

  Used by `iolanta --search "<notion>" --as jsonl`, which fans out to four
  linked-data search APIs (Wikidata Reconciliation, DBpedia Lookup,
  Nanopublications Lucene SAIL, and LOV term search) and emits one candidate
  URI per line.

  Each line carries the fields `uri`, `source`, `title`, `description`,
  `score`, and `types`. The `score` field is **per-source**, not
  cross-source: Wikidata reconciliation returns floats in [0, 1], the
  Nanopublications Lucene endpoint returns arbitrary positive floats, LOV
  uses its own scale, and DBpedia returns `null`. Compare scores within a
  single `source` value, never across.
---

{{ URIRef("https://iolanta.tech/datatypes/jsonl") | as('mkdocs-material') }}
