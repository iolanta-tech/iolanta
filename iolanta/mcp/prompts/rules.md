# How to author Linked Data with Iolanta

**R00.** Follow this YAML-LD authoring workflow:
- Draft YAML-LD from user text
- Use the Iolanta MCP `render_uri` tool with `as_format: labeled-triple-set` to validate and get feedback
- Address the feedback, correct the YAML-LD document appropriately

**R01.** Acceptance Criteria:

- The document fits the original statement the user wanted to express;
- No negative feedback is received.

**R02.** Use YAML-LD format, which is JSON-LD in YAML syntax, for writing Linked Data.

**R03.** Always quote the @ character in YAML since it's reserved. Use `"@id":` instead of `@id:`.

**R04.** Prefer YAML-LD Convenience Context which maps @-keywords to $-keywords that don't need quoting: `"@type"` → `$type`, `"@id"` → `$id`, `"@graph"` → `$graph`.

**R05.** Use the dollar-convenience context: `"@context": [https://json-ld.org/contexts/dollar-convenience.jsonld, ...]`

**R06.** Reduce quoting when not required by YAML syntax rules.

**R07.** Do not use mock URLs like `https://example.org`. Use resolvable URLs that preferably point to Linked Data.

**R08.** Use URIs that convey meaning and are renderable with Linked Data visualization tools. Search for appropriate URIs from sources like DBPedia or Wikidata.

**R09.** Use the Iolanta MCP `render_uri` tool with `as_format: mermaid` to generate Mermaid graph visualizations of Linked Data. If the user asks, you can save them to `.mmd` files for preview and documentation purposes.

**R10.** For language tags, use YAML-LD syntax: `rdfs:label: { $value: "text", $language: "lang" }` instead of Turtle syntax `"text"@lang`.

**R11.** Do not attach labels to external URIs that are expected to return Linked Data. Iolanta will fetch those URIs and render labels from the fetched data.

**R12.** Use `"@type": "@id"` in the context to coerce properties to IRIs instead of using `$id` wrappers in the document body.

**R13.** For software packages, use `schema:SoftwareApplication` as the main type rather than `codemeta:SoftwareSourceCode`.

**R14.** Use Wikidata entities for programming languages (e.g., `https://www.wikidata.org/entity/Q28865` for Python) instead of string literals.

**R15.** Use proper ORCID URIs for authors (e.g., `https://orcid.org/0009-0001-8740-4213`) and coerce them to IRIs in the context.

**R16.** For tools that provide both library and CLI functionality, classify as `schema:Tool` with `schema:applicationSubCategory: Command-line tool`.

**R17.** Use real, resolvable repository URLs (e.g., `https://github.com/iolanta-tech/python-yaml-ld`) instead of placeholder URLs.

**R18.** Include comprehensive metadata: name, description, author, license, programming language, version, repository links, and application category.

**R19.** Use standard vocabularies: schema.org, RDFS, RDF, DCTerms, FOAF, and CodeMeta when appropriate.

**R20.** Validate Linked Data using the Iolanta MCP `render_uri` tool with `as_format: labeled-triple-set` to check for URL-as-literal issues and proper IRI handling.

**R21.** Do not add `rdfs:label` to external URIs that are expected to return Linked Data. If a URI does not exist or cannot be resolved, do not mask this fact by adding labels. Instead, use a different, existing URI or document the issue with a comment.

**R22.** Define URI coercion in the context using `"@type": "@id"` rather than using `$id` wrappers in the document body. This keeps the document body clean and readable while ensuring proper URI handling.

**R23.** When defining local shortcuts for URIs in the context, use dashed-case (e.g., `appears-in`, `named-after`) instead of camelCase (e.g., `appearsIn`, `namedAfter`). This improves readability and follows common YAML conventions.
