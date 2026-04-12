# Tests

## Integration screenshots (`test_integration.py`)

**T01.** `generate_screenshot` runs Textual with `iolanta`, **writes** `docs/screenshots/<name>.svg`, then asserts the file is **git-tracked** and has **no working-tree diff** against the index. If the render differs from what is committed, the assertion fails—but the file on disk is usually **already updated**, which is what you `git add` after an intentional UI change.

**T02.** Each integration test also asserts **substrings** present in the SVG text (e.g. expected labels), not only that the screenshot file matches the repo baseline.

## SVG screenshot of Iolanta (Textual)

**T03.** From the repository root, use `textual run -c` so the app is started as a command, and pass Iolanta’s target (URL or file path) after `iolanta`. Match integration tests for terminal size and color:

```bash
LINES=34 COLUMNS=113 FORCE_COLOR=1 textual run -c \
  --screenshot 50 \
  --screenshot-path docs/screenshots \
  --screenshot-filename example.svg \
  iolanta 'https://example.org/your-resource'
```

- **`--screenshot`** — delay in seconds before capture.
- **`--screenshot-path`** — directory for the output (often `docs/screenshots`).
- **`--screenshot-filename`** — must end with `.svg` for vector output.
- Unset or override **`NO_COLOR`** so captures match colored CI output; integration tests set **`FORCE_COLOR=1`**.

**T04.** SVG naming for URLs/paths follows the same rules as `generate_screenshot` in `test_integration.py` (host, dotted path, optional fragment; local paths dotted relative to repo root).
