# AGENTS

## Commit Message Formatting Rules

**C00.** All commit messages must be one line only.

**C01.** Start every commit message with an issue ID prefix (e.g., `#348`). Do not include a colon after the issue ID.

**C02.** The first word after the issue ID must start with a capital letter.d

**C03.** Use ➕ emoji to indicate additions. Do not use the word "Add" when using this emoji.

**C04.** Use 🧹 emoji to indicate removals. Do not use the word "Remove" when using this emoji, as the emoji already conveys this meaning.

**C05.** Wrap code references (class names, method names, attributes, parameters, file paths, etc.) in backticks (e.g., `` `ClassName` ``, `` `method_name` ``, `` `attribute` ``).

**C06.** Use the → arrow symbol to indicate changes from one state/value to another (e.g., `A → B`, `` `str` → `URIRef` ``).

**C07.** Create one commit per file. Do not combine multiple files into a single commit unless explicitly requested.

**C08.** Use single quotes for commit messages (e.g., `git commit -m 'message'`) to avoid shell interpretation issues with backticks in code references.

**C09.** Before writing a commit message, always diff the file to understand what changed. Base the commit message on the actual changes, not generic terms like "Update". Use `git diff <file>` to see the changes.

**C10.** When committing new files, commit them one at a time. Never use `git add` with multiple files or directories. Always `git add <single-file>` then `git commit` for each file separately.

### Examples

✅ Correct:
- `#348 ➕ `Description` widget, `PageFooter`, & `properties_on_the_right` flag`
- `#348 🧹 Unused `render_all` method`
- `#348 Change `Location.url` type `str` → `NotLiteralNode``
- `#348 Bump version 2.1.7 → 2.1.8`
- `#348 Standardize namespace URLs `https://` → `http://``

❌ Incorrect:
- `#348: Add Description widget` (colon after issue ID, word "Add" instead of emoji)
- `#348 Remove unused method` (word "Remove" instead of 🧹 emoji)
- `#348 change Location.url type` (first word not capitalized, no backticks, no arrow)
- `#348 Add widget and fix bug` (multiple changes in one commit)

## Development Server

**D00.** To run the MkDocs development server, use `j serve`. The server runs on `http://localhost:6451`. Normally, the user already has it running for development.

**D01.** The `j serve` command runs `mkdocs serve -a localhost:6451` (note: the docstring incorrectly states port 9841, but the actual port is 6451).

**D02.** To verify roadmap rendering, use `iolanta {file} --as https://iolanta.tech/roadmap/datatypes/mermaid` where `{file}` is the path to a roadmap YAML-LD file (e.g., `docs/roadmap/iolanta-development-roadmap.yamlld`). This will render the roadmap as a Mermaid diagram showing tasks, events, bugs, and their blocking relationships.

**D03.** To validate that a roadmap renders to valid Mermaid syntax, use `iolanta {file} --as https://iolanta.tech/roadmap/datatypes/mermaid | mmdc -i - -o /dev/null` where `{file}` is the path to a roadmap YAML-LD file. This renders the roadmap and validates the Mermaid syntax using mmdc.

## Code Formatting and Linting

**F00.** To auto-format code according to the project's style rules, use `j fmt`. This command is provided by the `jeeves-yeti-pyproject` package.

**F01.** To lint code and check for style issues without formatting, use `j lint`. This command is also provided by the `jeeves-yeti-pyproject` package.

**F02.** WPS (wemake-python-styleguide) linting errors must be fixed, not dismissed. The project uses WPS for a reason - treat all WPS errors as issues that need to be addressed. Do not dismiss linting errors as "expected" or "normal".

**F03.** When running linters (`j lint`), they run against the entire project, not specific files. Fix all linting errors found, not just errors in files that were recently modified or mentioned.

**F04.** Never catch broad exceptions like `Exception` or `BaseException`. This is an antipattern that hides bugs, masks real problems, makes debugging harder, and violates the principle of catching only what you expect. Always catch specific exception types (e.g., `AttributeError`, `ValueError`, `KeyError`) that you actually expect and know how to handle. If you need to suppress a linting error about exception handling, use `# noqa` rather than changing the exception handling logic.

**F05.** Condense try...except blocks to minimize their size. Extract common error handling logic into helper functions rather than duplicating it across multiple exception handlers. Use tuple exception catching (e.g., `except (Error1, Error2) as error:`) when multiple exceptions are handled identically.

**F06.** Only put code in try blocks that can actually raise exceptions. Move operations that are unlikely or cannot raise exceptions (e.g., simple assignments, property access, object construction that doesn't involve I/O or parsing) outside of try blocks. This makes the code clearer about what can fail and reduces unnecessary exception handling overhead.

**F07.** A branch that should never execute must never exist. Remove defensive `else` branches, `assert False` statements, or similar "this should never happen" code paths. If the type system or logic guarantees a branch is unreachable, trust it and remove the unreachable code. If you're concerned about future changes, use type checking and tests instead of defensive runtime checks.

**F08.** Multiple if...elif branches with `isinstance()` calls must be replaced with `match/case` statements. The `match/case` syntax (Python 3.10+) is more readable, type-safe, and idiomatic for type-based dispatch. Use `match value: case Type():` instead of `if isinstance(value, Type): ... elif isinstance(value, OtherType): ...`.

**F09.** In tests, prefer repeated string literals over helper constants introduced only to satisfy string-reuse lint rules. If satisfying a lint rule would require structural refactoring, API changes, or other non-local reshaping, stop and ask first. In tests, prefer a targeted `# noqa` over abstractions created only to silence the linter.

**F10.** To suppress a WPS violation for an entire file (e.g. WPS202), add it to `.flake8` under `per-file-ignores` — do not use a module-level `# noqa` comment. Module-level `# noqa` does not work for file-wide WPS suppressions.

**F11.** Use `frozenset(("a", "b", ...))` with a tuple literal, not `frozenset({"a", "b", ...})` with a set literal. The set-literal form triggers WPS527.

## Adding Jeeves Commands

**J00.** Jeeves is a task runner based on Typer. To add a new development command, add a function to `jeeves/__init__.py`. Functions in this module automatically become commands accessible via `j <command-name>`.

**J01.** Function names use underscores (e.g., `def my_command()`), but are invoked with dashes: `j my-command` (Typer automatically converts underscores to dashes).

**J02.** Commands should:
- Have a docstring describing what they do (shown in `j --help`)
- Use the `sh` library for shell commands (e.g., `sh.mkdocs.serve(...)`)
- Use `console` from Rich for colored output (e.g., `console.print("[green]Success[/green]")`)
- Accept parameters as function arguments (Typer automatically creates CLI arguments)

**J03.** Example command:
```python
def build_docs():
    """Build documentation and deploy to GitHub Pages."""
    sh.mkdocs('gh-deploy', '--force', '--clean')
    console.print("[green]✅ Documentation deployed[/green]")
```

**J04.** For commands that wrap existing tools, prefer composing standard commands with pipes/redirection rather than creating a Jeeves command. Only create Jeeves commands when they add significant value (e.g., complex workflows, multiple steps, or project-specific logic).

**J05.** For `docs/blog/remote-contexts-considered-harmful/`, regenerate all derived tab artifacts with `j generate-remote-contexts-considered-harmful-artifacts`. Keep Mermaid diagrams inside tab partials pre-generated as `.mmd` files included from disk; do not rely on live Jinja Mermaid macros inside snippet-included partials.

## Rendering and Facets

**A00.** Before adding fallback logic to a generic facet, search for an existing specialized facet and use facet selection first. Do not hardcode domain-specific rendering in a general-purpose facet when a class-specific facet already exists.

**A01.** When introducing or changing a namespace canonical IRI, audit every redirect, resolver, and fetch path that depends on that namespace. A namespace change is incomplete until resolution behavior is verified end to end.

**A02.** A specialized renderer must not lose data the generic renderer already supports. If the generic Mermaid facet renders blank nodes, a specialized Mermaid facet must render them too unless omission is explicitly requested.

**A03.** For remote RDF sources, verify the actual content-negotiated payload before making schema assumptions. Do not infer predicates or `rdf:type` values for ORCID, Wikidata, or similar sources from memory.

**A04.** In Mermaid, do not reuse a real subgraph ID as an edge endpoint from inside another subgraph. Mermaid may reinterpret that as containment and nest graphs incorrectly.

**A05.** When using Mermaid HTML labels, validate both the generated Mermaid source and a rendered SVG or PNG. Syntax acceptance alone is not sufficient; inspect the actual visual output.

**A06.** If a rendering change is about layout or readability, inspect the rendered artifact yourself before claiming it is fixed.

**A07.** Keep regression tests aligned with the intended architecture, not just the observed final string output. For example, when relevant, test that the specialized facet is selected rather than only asserting the rendered text.

**A08.** When debugging facet selection, SPARQL, or graph shape for YAML-LD or JSON-LD you have as a file, run `pyld to-rdf` on that document and inspect the triples before asserting which predicates or literals exist. Do not infer graph content from memory. For remote sources, **A03** still applies.

## Prose and documentation

**P00.** DRY: no duplicated facts, lists, or citations—say each once, in the right place.

**P01.** Quote external sources exactly. Preserve in-text links from the source, and use a full sentence unless the excerpt is explicitly marked as partial.

**P02.** Keep prose terse by default. Prefer source quote, necessary example, and concrete tradeoffs; remove explanations that repeat nearby quotes, tables, headings, or examples.

**P03.** For tabbed MkDocs documentation, prefer normal Markdown `===` tabs over hand-written raw HTML tab markup when possible. Raw HTML tabs plus nested Markdown/HTML blocks are fragile and harder to maintain.

**P04.** In snippet-included Markdown partials (`--8<--`), do not rely on live Jinja expressions being rendered. If a tab body needs dynamic output such as Mermaid, pre-generate the artifact and include the generated file instead.

**P05.** Hidden dotfile Markdown partials placed next to an `index.md` page are acceptable for local snippet includes in this docs setup and do not become standalone MkDocs pages.

## Subdirectory guidance

- [tests/AGENTS.md](tests/AGENTS.md) — integration screenshot tests, SVG capture via Textual + `iolanta`
- [docs/howto/nanopublish-with-llm/AGENTS.md](docs/howto/nanopublish-with-llm/AGENTS.md) — YAML-LD / Linked Data authoring for nanopublishing
