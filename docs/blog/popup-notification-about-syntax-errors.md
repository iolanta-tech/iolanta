---
date: "2025-02-19"
title: Show a popup notification for syntax errors
---

# Context

Iolanta automatically reloads YAML-LD files upon changes. If the file contains a syntax error, Iolanta silently ignores it, leading to an empty or misleading view. Currently, the only way to diagnose such errors is by opening the console (F12), which is not an ideal user experience.

Several approaches to surface syntax errors have been considered:

1. **Modifying Existing Facets**: Each facet (e.g., Properties, Inverse Properties, Graph Triples) would need to handle syntax errors separately, displaying an explicit error message instead of their usual content.
2. **Creating a Special "Syntax Error" Facet**: When a syntax error is detected, Iolanta would display this facet as an option in the status bar.
3. **Displaying a Popup Notification**: A notification widget would appear in the bottom right corner of the screen whenever a syntax error occurs.

# Decision

Iolanta will display a popup notification when it encounters a syntax error in the YAML-LD file. This notification will be a standard Textual widget and will appear in the bottom right corner of the screen.

# Consequences

## Pro
- **Immediate visibility**: The error is surfaced without requiring user action (e.g., switching facets or opening the console).
- **Non-intrusive**: The popup does not interfere with existing facets or workflows.
- **Consistency**: Centralizes error handling in a single mechanism instead of modifying multiple facets.
- **Ease of implementation**: Textual provides built-in support for notifications, simplifying the implementation.

## Contra
- **Transient nature**: If the notification disappears too quickly, users might miss it.
- **Potential distraction**: If errors occur frequently, popups may become an annoyance.
- **No persistent log**: Unlike the console, the popup does not retain a history of past errors.

To mitigate these issues, a configurable timeout for the notification duration may be introduced, and the error could optionally be logged for later retrieval.
