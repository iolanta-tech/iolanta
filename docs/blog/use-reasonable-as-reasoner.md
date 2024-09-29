---
title: Use ... as reasoner
date: 2024-09-29
---

## Context

The whole application freezes while we are running OWL RL reasoning because that operation is CPU bound and threading does not work well with it.

```mermaid
graph LR
    what(What do we do?) --> another("Use another reasoner")

    another --> reasonable("<code>reasonable</code>")
    click reasonable "https://github.com/gtfierro/reasonable"
    reasonable <-- "➕" --- reasonable-python("Has Python bindings")
    reasonable <-- "➖" --- reasonable-error("<code>BlankNodeIdParseError</code>") <-- "is solved with" --- blank-node-format("Format blank nodes<br/>without special characters")
```

## Decision

Use `reasonable`.

## Consequences

### Pro

* Much faster reasoning!
* No noticeable freezes

### Contra

* Some triple duplications which we shall fix
