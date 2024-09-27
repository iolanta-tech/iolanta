---
title: Use ... for interactive mode
---

## Context

We have two main modes of operation:

* **non-interactive**, where `iolanta` command will render what it was asked to and quits,
* and **interactive**, where a terminal window allows to navigate among IRIs of the Cyberspace.

There are a lot of parameters common to these modes, for instance:

* `project_directory` to read files from,
* `cache_directory` to write downloaded files to.

{% verbatim %}
{{ render("interactive-mode-alternatives") }}
{% endverbatim %}

## Decision

Use one command for now.

## Consequences

Invent a special environment for the browser main rendering area.
