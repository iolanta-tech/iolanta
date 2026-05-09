---
title: Choose Markdown pre-rendering pipeline for Iolanta-backed Linked Data insertion
status: decided
date: "2026-05-09"
tags: [decision]
hide:
  - toc
---

# Choose Markdown pre-rendering pipeline for Iolanta-backed Linked Data insertion

## Context

I want to author printable documents as Markdown while using Iolanta to insert rendered Linked Data fragments into the document. The Linked Data may come from local YAML-LD files, project data, installed Iolanta facilities, nanopublication discovery, or normal web loading. The Markdown source may contain Jinja2 markup that calls Iolanta, similar to the filters and macros currently wired through `main.py`. The immediate output should be plain rendered Markdown that can be read in Typora or passed to a later PDF pipeline. PDF generation is intentionally a follow-up decision; this decision is about producing the pre-rendered Markdown artifact.

### Alternatives Considered

- `iolanta --render-template` with Jinja2 and Iolanta helpers
- Standalone Python script based on `main.py`
- MkDocs preprocessing step
- Markdown extension syntax instead of Jinja2
- Pandoc filter before Markdown output
- Manual copy-paste of Iolanta output

## Decision

=== ":white_check_mark: `iolanta --render-template` with Jinja2 and Iolanta helpers"

    Add a `--render-template` mode to the existing `iolanta` command:

    ```bash
    iolanta --render-template source.jinja2.md > source.output.md
    ```

    It takes a `.jinja2.md` file, evaluates Jinja2 with registered helpers for Iolanta rendering, SPARQL, and path or IRI conversion, lets those helpers use normal Iolanta facilities including project data and web loading, and prints rendered Markdown to stdout.

    <div class="grid" markdown>
    <div markdown>
    #### Pro

    - Directly solves the core problem: document-embedded calls can invoke Iolanta while the output remains plain Markdown.
    - Preserves the current `iolanta FILE --as ...` UX because no Typer subcommand group is introduced.
    - Reuses the successful `main.py` model without requiring MkDocs to be present in the authoring workflow.
    - Keeps PDF conversion independent, so Typora, Pandoc, browser printing, or another backend can be evaluated later.
    - Gives the project one explicit mode that can validate inputs, fail clearly, and be tested.
    </div>

    <div markdown>
    #### Contra

    - Requires designing a small public template-helper surface instead of relying on whatever happens to exist in `main.py`.
    - Needs careful path conventions for source Markdown and project roots.
    - Adds another mutually exclusive mode to the existing `iolanta` command, so option validation must stay explicit.
    </div>
    </div>

=== ":x: Standalone Python script based on `main.py`"

    A standalone script is useful for prototyping, but it should not be the selected interface. The document renderer needs to run in other repositories after installing Iolanta, and it needs an explicit, documented command shape.

    <div class="grid" markdown>
    <div markdown>
    #### Pro

    - Fastest route to a working prototype.
    - Preserves the current mental model almost exactly.
    - Useful for discovering the minimal helper API before committing to a stable command.
    </div>

    <div markdown>
    #### Contra

    - Easy to leave as a one-off script with unclear input/output conventions.
    - Harder to document, test, and reuse across multiple printable documents.
    - Does not preserve a stable command interface for future PDF generation.
    </div>
    </div>

=== ":x: MkDocs preprocessing step"

    MkDocs preprocessing is the right model for website pages, but not for standalone printable documents. The pre-renderer should run in a repository that contains the document and data, without requiring that repository to be an MkDocs site.

    <div class="grid" markdown>
    <div markdown>
    #### Pro

    - Reuses the exact integration style already used for documentation pages.
    - Keeps `main.py` as the single place where Iolanta-backed macros and filters are registered.
    - Fits documents that are also meant to appear on the website.
    </div>

    <div markdown>
    #### Contra

    - Couples printable-document authoring to the website build system.
    - Makes a standalone `.output.md` workflow less direct.
    - MkDocs page context may leak into documents that are intended to be printed rather than published as site pages.
    </div>
    </div>

=== ":x: Markdown extension syntax instead of Jinja2"

    This would require inventing and parsing a new syntax before calling Iolanta, even though the desired source format is already Jinja2-flavored Markdown.

=== ":x: Pandoc filter before Markdown output"

    Pandoc can transform parsed documents, but it does not naturally evaluate Jinja2 macros or call the existing Iolanta helper model. This is more appropriate after Markdown is pre-rendered, when deciding how to produce PDF.

=== ":x: Manual copy-paste of Iolanta output"

    Manual insertion loses repeatability, makes the Linked Data sidecars less useful, and cannot reliably regenerate a printed document when the data changes.

## Consequences

- The first implementation should separate Markdown pre-rendering from PDF generation.
- The existing `iolanta FILE --as ...` command shape must remain valid.
- `--render-template`, `--query`, `--search`, and positional URL rendering should be mutually exclusive modes of the same command.
- The source document can use `.jinja2.md`; rendered artifacts can be created with shell redirection when needed.
- Local YAML-LD files are one possible input, not a requirement; templates may use normal Iolanta resolution and web loading.
- The pre-renderer needs explicit conventions for resolving document-relative paths and choosing `Iolanta.project_root`.
- When running in another repository, `Iolanta.project_root` should default to that repository or working directory, with an explicit override if needed.
- The helper API should start from the current `main.py` operations but become a stable author-facing interface.
- Errors from Iolanta rendering should fail the pre-rendering command clearly enough to fix the source document or YAML-LD data.

#### Implementation Steps

- [ ] Define input naming conventions for `.jinja2.md`.
- [ ] Extract the current `main.py` macro and filter registration into reusable code or mirror it in a small pre-rendering module.
- [ ] Add a `--render-template` option to the existing `iolanta` command.
- [ ] Validate that `--render-template`, `--query`, `--search`, and positional URL rendering are mutually exclusive.
- [ ] Define how the command chooses `Iolanta.project_root`, and add an override if the default is not enough.
- [ ] Add fixture tests that prove Jinja2 calls can render Iolanta output from local YAML-LD and from normal project-root resolution.
- [ ] Defer Typora, Pandoc, browser printing, and direct PDF generation to a separate PDF pipeline decision.
