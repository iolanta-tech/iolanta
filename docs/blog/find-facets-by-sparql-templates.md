---
title: Find facets by SPARQL patterns
$type: ADR
date: "2025-04-20"
hide: [toc]
---

# Find facets by SPARQL patterns

I need to be able to call `PropertyPairsFacet` for each node which appears in a predicate position. The facet will render all subject-object pairs for this property as a table.

=== ":white_check_mark: Decision: Use SPARQL"

    ```yaml
    $id: python://iolanta.facets.PropertyPairsFacet
    iolanta:outputs: datatypes:textual
    iolanta:pattern: ASK { ?subject $this ?object }
    ```

    ## :fast_forward: Consequences
    
    <div class="grid" markdown>
    <div markdown>
    ### :heavy_plus_sign: Pro
    
    * Simple and clear implementation
      * No dependency on SHACL processing overhead
    </div>
    <div markdown>
    ### :heavy_minus_sign: Contra
    * Patterns are not Linked Data
        * And therefore cannot be easily reused and extended
        * :bulb: But this can be amended later by support for a RDF based SPARQL serialization
    </div>
    </div>
  
=== ":x: SHACL"

    Not supported by [SHACL Core](https://www.w3.org/TR/shacl):

    > SHACL Core includes the following kinds of targets: node targets, class-based targets (including implicit class-based targets), subjects-of targets, and objects-of targets.

    There are no `predicates-as` targets, as we can see.

=== ":x: SHACL-SPARQL"

    ```yaml title="Courtesy of ChatGPT"
    $id: https://example.com/shapes/PredicateNodeShape
    $type: sh:NodeShape
    sh:sparql:
      $type: sh:SPARQLConstraint
      sh:message: "Node must appear in predicate position."
      sh:ask: |-
        ASK {
          ?subject $this ?object .
        }
    ```

    If we have to use SPARQL anyway then I do not see the need to employ SHACL as an intermediate layer wrapping it.
