# Documentation

## Prose and documentation

**P00.** DRY: no duplicated facts, lists, or citations—say each once, in the right place.

**P01.** Quote external sources exactly. Preserve in-text links from the source, and use a full sentence unless the excerpt is explicitly marked as partial.

**P02.** Keep prose terse by default. Prefer source quote, necessary example, and concrete tradeoffs; remove explanations that repeat nearby quotes, tables, headings, or examples.

**P03.** For tabbed MkDocs documentation, prefer normal Markdown `===` tabs over hand-written raw HTML tab markup when possible. Raw HTML tabs plus nested Markdown/HTML blocks are fragile and harder to maintain.

**P04.** In snippet-included Markdown partials (`--8<--`), do not rely on live Jinja expressions being rendered. If a tab body needs dynamic output such as Mermaid, pre-generate the artifact and include the generated file instead. After editing a diagram source file, run `j generate-docs-mermaid`.

**P05.** Hidden dotfile Markdown partials placed next to an `index.md` page are acceptable for local snippet includes in this docs setup and do not become standalone MkDocs pages.

**P06.** In documentation prose, format GitHub issue and pull request links with the GitHub Material icon, e.g. `[:material-github: owner/repo#123](https://github.com/owner/repo/issues/123)`.

## Agent guidance files

**P07.** MkDocs builds every `*.md` under `docs/` unless excluded. Add `**/AGENTS.md` to `exclude_docs` in `mkdocs.yml` so agent guidance files are not published as site pages.

## YAML-LD examples

**P08.** Do not use `@graph` / `$graph` in docs YAML-LD examples. Prefer a top-level `"@id"` document with nested objects for related blank nodes.

**P09.** Push typing, language, and reference coercion into `@context` term definitions — never inline in the document body when context can express it. Use `"@type": xsd:…` on property terms for typed literals, `"@language": …` for language-tagged strings, and `"@type": "@id"` for properties that point to nodes. Keep the document body to bare values, nesting, and `"@id"` where a stable blank-node label is needed. Never use a bare `_:name` scalar as a property value — without `"@type": "@id"` in context it becomes an `xsd:string` literal.
