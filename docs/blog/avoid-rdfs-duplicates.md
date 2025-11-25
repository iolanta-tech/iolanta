---
title: Avoid duplicate RDFS ontologies by …
date: 2024-08-31
tags: [decision]
---

## Context

Due to [:material-stack-overflow: a bug in OWL2](https://stackoverflow.com/questions/78934864/owl2-ontology-creates-a-ghost-rdfs-ontology-due-to-missing), we've got two URLs claiming to be ontologies:

- http://www.w3.org/2000/01/rdf-schema
- http://www.w3.org/2000/01/rdf-schema#

!!! info "Also"
    A similar predicament exists for OWL ontology itself. We've got two URLs: with and without the :octicons-hash-24: sign.

What alternatives do we have?


<div class="grid cards" markdown>

-   :bulb:{ .lg .middle } __Filter `owl:Ontology` instance list by `rdfs:isDefinedBy` links__

    ---

    Only show ontologies which define at least one term.

    !!! danger "This does not solve the OWL problem."

-   :bulb:{ .lg .middle } __Rewrite URLs while loading them__

    ---

    Replace `…owl` with `…owl#`.

</div>

## Decision

Rewrite URLs.

## Consequences

➕ Should resolve both problems at once.
