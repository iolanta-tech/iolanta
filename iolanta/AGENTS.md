# Iolanta package

## Rendering and Facets

**A00.** Before adding fallback logic to a generic facet, search for an existing specialized facet and use facet selection first. Do not hardcode domain-specific rendering in a general-purpose facet when a class-specific facet already exists.

**A01.** When introducing or changing a namespace canonical IRI, audit every redirect, resolver, and fetch path that depends on that namespace. A namespace change is incomplete until resolution behavior is verified end to end.

**A02.** A specialized renderer must not lose data the generic renderer already supports. If the generic Mermaid facet renders blank nodes, a specialized Mermaid facet must render them too unless omission is explicitly requested.

**A03.** For remote RDF sources, verify the actual content-negotiated payload before making schema assumptions. Do not infer predicates or `rdf:type` values for ORCID, Wikidata, or similar sources from memory.

**A04.** In Mermaid, do not reuse a real subgraph ID as an edge endpoint from inside another subgraph. Mermaid may reinterpret that as containment and nest graphs incorrectly.

**A05.** When using Mermaid HTML labels, validate both the generated Mermaid source and a rendered SVG or PNG. Syntax acceptance alone is not sufficient; inspect the actual visual output.

**A06.** If a rendering change is about layout or readability, inspect the rendered artifact yourself before claiming it is fixed.

**A07.** Keep regression tests aligned with the intended architecture, not just the observed final string output. For example, when relevant, test that the specialized facet is selected rather than only asserting the rendered text.

**A08.** When debugging facet selection, SPARQL, or graph shape for YAML-LD or JSON-LD you have as a file, run `pyld to-rdf` on that document and inspect the triples before asserting which predicates or literals exist. Do not infer graph content from memory. For remote sources, **A03** still applies.

**A09.** Do not hand-edit generated prefix data in `iolanta/data/prefixes.yamlld`; use a separate non-generated data file for local prefix overrides.

**A10.** Visualization overlays in `docs/visualizations/` are published to `https://iolanta.tech/visualizations/` by MkDocs. At runtime, Iolanta discovers visualization metadata via nanopublications (`iolanta/discovery/visualization_nanopublications.py`); the local `docs/visualizations/` files are not loaded at runtime.

## Roadmap CLI verification

**D02.** To verify roadmap rendering, use `iolanta {file} --as https://iolanta.tech/roadmap/datatypes/mermaid` where `{file}` is the path to a roadmap YAML-LD file (e.g., `docs/roadmap/iolanta-development-roadmap.yamlld`). This will render the roadmap as a Mermaid diagram showing tasks, events, bugs, and their blocking relationships.

**D03.** To validate that a roadmap renders to valid Mermaid syntax, use `iolanta {file} --as https://iolanta.tech/roadmap/datatypes/mermaid | mmdc -i - -o /dev/null` where `{file}` is the path to a roadmap YAML-LD file. This renders the roadmap and validates the Mermaid syntax using mmdc.
