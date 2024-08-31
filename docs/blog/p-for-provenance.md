---
title: Press P to see provenance
tags: [decision]
date: 2024-08-27
---

# Do … to see provenance

## Context

When we see a statement in Iolanta a very basic operation would be to understand where that statement comes from. For instance, if RDFS ontology contains `rdfs:seeAlso` then who said it does? The RDFS itself or it was a mistake from some other source?

### Provenance Mode

Provenance Mode is a mode in the UI which is focused on provenance, on understanding the source of each statement. This deserves its own mode because, in the light of the AAA principle (Anyone can say Anything about Any subject), it is of paramount importance to see where each piece of information comes from.

In Provenance mode, each link displayed in the UI must point to a piece of provenance information about something. Click or `Enter` on a link will lead to a page with such information.

In normal mode, a piece of text might not be a link; in Provenance mode, it will become one, to show where this piece of text arrived.

Vice versa, something that's a link in normal mode can become plain text in Provenance mode if provenance for it is not applicable.

How to switch to, and from, Provenance Mode? We've got alternatives.

### :one: Press & hold `Alt`

Provenance Mode will be active while `Alt` key is held.

### :two: Press & release `P`

This will switch to Provenance mode or back to Normal mode.


## Decision

**Implement Provenance Mode Toggle with `P` Key:**
- Pressing and releasing the `P` key will switch to Provenance Mode. Pressing `P` again will return to Normal Mode.

## Consequences

### Pros:
1. **Ease of Use**: Users can easily switch modes with a simple key press, making it intuitive and accessible.
2. **Toggle Flexibility**: The toggle allows users to remain in Provenance Mode without holding down a key, reducing finger strain during longer sessions.
3. **Consistency**: The `P` key is easy to remember (`P` for Provenance), aligning with standard keyboard shortcuts.
4. **No Conflict**: This solution avoids conflicts with other potential keyboard shortcuts that might be used for navigation or other UI actions.

### Cons:
1. **Mode Confusion**: Users might forget which mode they're in, leading to potential confusion, especially if the visual indicators of mode change are subtle.
2. **Accidental Activation**: Users might accidentally switch modes if they press `P` unintentionally, potentially disrupting their workflow.
3. **Mode Persistence**: If users frequently need to check provenance and then revert to normal viewing, the toggle may require extra key presses compared to a press-and-hold approach, slightly reducing efficiency.
