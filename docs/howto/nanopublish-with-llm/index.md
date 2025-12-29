# Nanopublishing with Cursor AI IDE & Iolanta

## What is a Nanopublication?

…

## Choice of tools

…

??? note "Why Cursor AI IDE?"
    <table>
      <thead>
        <tr>
          <th>Tool</th>
          <th>Decision</th>
          <th>Reason</th>
          <th>Version Evaluated</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>Cursor IDE</th>
          <td>Yes</td>
          <td>No issues found so far</td>
          <td>Current @ 2025-09-18</td>
        </tr>
        <tr>
          <th>JetBrains IDE + JetBrains AI Assistant</th>
          <td>No</td>
          <td>Cannot run a command and directly consume its output, we have to resort to copy-paste, which is not ergonomic at all.</td>
          <td>2025.2.0.1</td>
        </tr>
      </tbody>  
    </table>

## Choosing a topic

A good nanopublication topic should express a **single, clear knowledge claim** that can stand alone and be verified. The assertion should be:

- **Focused** — One main statement or relationship
- **Verifiable** — Based on facts, sources, or established knowledge
- **Self-contained** — Understandable without external context
- **Structured** — Can be expressed using Linked Data vocabularies and URIs

### Good topics

- Factual relationships: "Rhysling crater is named after the fictional character Rhysling"
- Scientific claims: "TRAPPIST-1 system has 7 planets"
- Taxonomic statements: "Pluto is not a planet"
- Domain-specific knowledge: "Mosquitoes bite humans"

### What to avoid

- Multiple unrelated claims in one assertion
- Vague or ambiguous statements
- Opinions without factual basis
- Topics that require extensive external context to understand

### Identifying suitable topics

Look for statements that:
1. Connect entities (people, places, concepts) with clear relationships
2. Can be expressed using standard vocabularies (Schema.org, DBpedia, Wikidata)
3. Have resolvable URIs for the entities involved
4. Make a meaningful contribution to a knowledge graph

## Claim

```markdown
--8<-- "docs/howto/nanopublish-with-llm/rhysling-crater-v0.md"
```

Then, we are asking the editor in the chat:

> Convert this into an LD document.

After some thinking, the document changes to this:

```markdown
--8<-- "docs/howto/nanopublish-with-llm/rhysling-crater-v1.md"
```

!!! warning "Not working further"
    We have a `pyld` bug which prevents this document from being renderable in Iolanta. We'll fix it.
