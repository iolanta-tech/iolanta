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
