# AGENTS

## Commits

Use the `commit` skill when creating git commits.

## Environment

**D04.** Run Python and MkDocs through direnv: `direnv exec . python …`, `direnv exec . mkdocs …`. Do not call `.venv/bin/python` directly — the venv is not set up correctly outside direnv's environment.

## Code Formatting and Linting

**F00.** To auto-format code according to the project's style rules, use `j fmt`. This command is provided by the `jeeves-yeti-pyproject` package.

**F01.** To lint code and check for style issues without formatting, use `j lint`. This command is also provided by the `jeeves-yeti-pyproject` package.

**F02.** WPS (wemake-python-styleguide) linting errors must be fixed, not dismissed. The project uses WPS for a reason - treat all WPS errors as issues that need to be addressed. Do not dismiss linting errors as "expected" or "normal".

**F03.** `j lint` runs flake8/ruff only on files changed against `origin/master` (`list_changed_files()` in `jeeves_yeti_pyproject`); untracked new files are excluded until they are at least staged. Mypy, by contrast, runs project-wide and the project tolerates a baseline (CI compares PR count vs master). When validating after a refactor, check flake8 is clean on the touched files; do not treat the long mypy tail as a regression unless the count grew.

**F04.** Never catch broad exceptions like `Exception` or `BaseException`. This is an antipattern that hides bugs, masks real problems, makes debugging harder, and violates the principle of catching only what you expect. Always catch specific exception types (e.g., `AttributeError`, `ValueError`, `KeyError`) that you actually expect and know how to handle. If you need to suppress a linting error about exception handling, use `# noqa` rather than changing the exception handling logic.

**F05.** Condense try...except blocks to minimize their size. Extract common error handling logic into helper functions rather than duplicating it across multiple exception handlers. Use tuple exception catching (e.g., `except (Error1, Error2) as error:`) when multiple exceptions are handled identically.

**F06.** Only put code in try blocks that can actually raise exceptions. Move operations that are unlikely or cannot raise exceptions (e.g., simple assignments, property access, object construction that doesn't involve I/O or parsing) outside of try blocks. This makes the code clearer about what can fail and reduces unnecessary exception handling overhead.

**F07.** A branch that should never execute must never exist. Remove defensive `else` branches, `assert False` statements, or similar "this should never happen" code paths. If the type system or logic guarantees a branch is unreachable, trust it and remove the unreachable code. If you're concerned about future changes, use type checking and tests instead of defensive runtime checks.

**F08.** Multiple if...elif branches with `isinstance()` calls must be replaced with `match/case` statements. The `match/case` syntax (Python 3.10+) is more readable, type-safe, and idiomatic for type-based dispatch. Use `match value: case Type():` instead of `if isinstance(value, Type): ... elif isinstance(value, OtherType): ...`.

**F10.** To suppress a WPS violation for an entire file (e.g. WPS202), add it to `.flake8` under `per-file-ignores` — do not use a module-level `# noqa` comment. Module-level `# noqa` does not work for file-wide WPS suppressions.

**F11.** Use `frozenset(("a", "b", ...))` with a tuple literal, not `frozenset({"a", "b", ...})` with a set literal. The set-literal form triggers WPS527.

**F12.** After changing Python code, run `j fmt` and then `j lint`. Fix lint findings in touched files before reporting completion; if `j lint` still fails because of unrelated project-wide errors, report that clearly.

## Subdirectory guidance

- [docs/AGENTS.md](docs/AGENTS.md) — prose/style, blog artifact regeneration
- [iolanta/AGENTS.md](iolanta/AGENTS.md) — facets, Mermaid rendering, SPARQL/graph debugging, roadmap CLI verification
- [jeeves/AGENTS.md](jeeves/AGENTS.md) — `j serve`, adding `j` commands
- [tests/AGENTS.md](tests/AGENTS.md) — integration screenshots, SVG capture, test linting
- [docs/howto/nanopublish-with-llm/AGENTS.md](docs/howto/nanopublish-with-llm/AGENTS.md) — YAML-LD / Linked Data authoring for nanopublishing
