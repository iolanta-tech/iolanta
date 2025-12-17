# Commit Message Formatting Rules

**C00.** All commit messages must be one line only.

**C01.** Start every commit message with an issue ID prefix (e.g., `#348`). Do not include a colon after the issue ID.

**C02.** The first word after the issue ID must start with a capital letter.

**C03.** Use ➕ emoji to indicate additions. Do not use the word "Add" when using this emoji.

**C04.** Use 🧹 emoji to indicate removals. Do not use the word "Remove" when using this emoji, as the emoji already conveys this meaning.

**C05.** Wrap code references (class names, method names, attributes, parameters, file paths, etc.) in backticks (e.g., `` `ClassName` ``, `` `method_name` ``, `` `attribute` ``).

**C06.** Use the → arrow symbol to indicate changes from one state/value to another (e.g., `A → B`, `` `str` → `URIRef` ``).

**C07.** Create one commit per file. Do not combine multiple files into a single commit unless explicitly requested.

## Examples

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
