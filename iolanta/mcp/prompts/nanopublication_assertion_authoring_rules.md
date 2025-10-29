# How to author Nanopublication Assertions with Iolanta

## What are Nanopublications?

Nanopublications are a special type of Linked Data that contain structured knowledge statements with three main components:

1. **Assertion** - The core knowledge claim or statement
2. **Provenance** - Information about how the assertion was derived (sources, methods, contributors)
3. **Publication Info** - Metadata about the nanopublication itself (author, creation date, etc.)

Nanopublications are cryptographically signed and published in the decentralized **Nanopublication Registry**, making them:
- Irrevocably attributed to the author
- Protected from tampering
- Referenceable by unique IDs
- Machine readable and reusable
- Decentralized and persistent

## Assertion-Only Workflow

**NP00.** Nanopublication assertion graphs must also satisfy the general rules for Linked Data authoring and workflow. That is provided in the MCP prompt named `ld_authoring_rules`.

**NP01.** We focus only on writing the **assertion graph** of the nanopublication.

**NP02.** Follow the standard YAML-LD authoring rules (R00-R23) for creating the assertion.

**NP03.** The assertion should express a single, clear knowledge claim that can stand alone.

**NP04.** Use proper Linked Data vocabularies and resolvable URIs for all entities and relationships.

**NP05.** After the assertion graph is ready, follow this workflow:

```bash
# Expand the YAML-LD to JSON-LD
pyld expand assertion.yamlld > expanded.jsonld

# Create nanopublication from the assertion
np create from-assertion expanded.jsonld > nanopublication.trig

# Publish the nanopublication (when ready)
np publish nanopublication.trig
```

**NP06.** The `pyld expand` command converts YAML-LD to expanded JSON-LD format.

**NP07.** The `np create from-assertion` command automatically generates the provenance and publication info components.

**NP08.** The `np publish` command cryptographically signs and publishes the nanopublication to the registry.

**NP09.** Use the Iolanta MCP `render_uri` tool to validate the assertion before proceeding with the workflow.

**NP10.** Save Mermaid visualizations of the assertion for documentation purposes.

## Best Practices for Assertions

**NP11.** Keep assertions focused on a single, verifiable claim.

**NP12.** Use canonical URIs from established knowledge bases (DBpedia, Wikidata, etc.).

**NP13.** Include sufficient context and metadata to make the assertion meaningful.

**NP14.** Ensure the assertion can be understood independently of external context.

**NP15.** Use standard vocabularies and well-established ontologies for relationships.
