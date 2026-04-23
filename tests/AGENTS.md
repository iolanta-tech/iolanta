# Tests

## Integration screenshots (`test_integration.py`)

**T01.** `generate_screenshot` runs Textual with `iolanta`, writes a temporary SVG, then compares stable SVG text against the committed `docs/screenshots/<name>.svg` baseline. Do not use raw `git diff` for screenshot assertions: Textual SVGs contain randomized IDs/classes, transient loading markers, and unstable text coordinates.

**T02.** Each integration test also asserts **substrings** present in the SVG text (e.g. expected labels), not only that the screenshot file matches the repo baseline.

**T03.** On mismatch, the assertion writes the raw generated SVG to `/tmp/iolanta-screenshot-failures/<name>.svg` and prints a unified diff of stable visible text. Inspect that file before deciding whether to update the committed baseline.

## SVG screenshot of Iolanta (Textual)

**T04.** From the repository root, use `textual run -c` so the app is started as a command, and pass Iolanta’s target (URL or file path) after `iolanta`. Match integration tests for terminal size and color:

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

**T05.** SVG naming for URLs/paths follows the same rules as `generate_screenshot` in `test_integration.py` (host, dotted path, optional fragment; local paths dotted relative to repo root).
