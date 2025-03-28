---
title: Roadmap
hide:
    - toc
    - navigation
---

# :octicons-project-roadmap-24: Roadmap

Roadmap of Iolanta development shows known yet unsolved bugs and to-do items. Some of them are clickable: they already have their GitHub issues associated to them.

!!! info "This roadmap is incomplete"
    If you have more ideas how to achieve happiness — you are more than welcome to contribute them!    

```mermaid
graph LR
    happiness("🚀 Happiness!")
    classDef happiness fill:#6f6,color:#080,stroke:#080,stroke-width:1px;
    class happiness happiness
    
    generate-roadmap("Generate this roadmap<br/>from LD") --> happiness
    
    nanopub-blog-post("Blog post:<br/><strong>Nanopublishing with Iolanta</strong>") --> markdown-nanopub-blog-post("Blog post:<br/><strong>Quick & readable Nanopublications with Markdown-LD") --> happiness
    
    nanopub-rs-graph("Publish an assertion from file<br/>@ <code>nanopub-rs</code>") --> nanopub-yaml-ld("Publish a YAML-LD assertion<br/>@ <code>nanopub-rs</code>") --> nanopub-blog-post
    
    subgraph "YAML-LD nanopublication on the front page"
        direction LR
        nanopublication-is-not-satisfactory("Nanopublication on front page<br/>is not satisfactory")
        class nanopublication-is-not-satisfactory bug
        
        literal-clickable("YAML-LD literal is clickable") --> nanopublication-is-not-satisfactory
        click literal-clickable "https://github.com/iolanta-tech/iolanta/issues/260"
        class literal-clickable bug
        
        fip-term-messy("<strong>Knowledge representation language</strong><br/>display is messy") --> nanopublication-is-not-satisfactory
        class fip-term-messy bug
        
        spec("YAML-LD spec is a URL<br/>not title") --> nanopublication-is-not-satisfactory
        class spec bug
    end
    
    subgraph "YAML-LD spec"
        spec-not-ld("Spec does not expose LD") --> spec
        class spec-not-ld bug

        rel-alternate("Spec does not show<br/>a rel=alternate link") --> spec-not-ld
        class rel-alternate bug
        
        w3c-license("https://purl.org/NET/rdflicense/W3C1.0.ttl<br/>crashes python-yaml-ld") --> spec-not-ld
        class w3c-license bug
        
        mismatch("Browsing <code>spec/data/spec.yaml</code><br/>≠ browsing the spec on the web") --> spec-not-ld
        class mismatch bug

        gig("Graph view shows <code>iolanta:Graph</code><br/>Should be in meta") --> spec-not-ld
        class gig bug
        
        last-loaded-time("<code>iolanta:last-loaded-time</code><br/>is not rendered") --> spec-not-ld
        class last-loaded-time bug
        
        spec-toc("Spec does not have a table of contents") --> spec-not-ld
        class spec-toc bug
        
        more("Invent more things<br/>to add to the YAML-LD representation<br/>of the spec") --> spec-not-ld
        
        prefixes("Source recommended prefixes<br/>for vocabs from somewhere") --> spec-not-ld
    end
    
    nanopublication-is-not-satisfactory --> nanopub-blog-post
    
    python-yaml-ld-markdown-ld("➕ Markdown-LD parser<br/>@ <code>python-yaml-ld</code>") --> markdown-ld("Edit a Markdown-LD document") --> markdown-nanopub-blog-post
    click markdown-ld "https://github.com/iolanta-tech/iolanta/issues/261"
        
    classDef bug fill:#f96,color:#f00,stroke:#f00,stroke-width:1px;
```

!!! success "Or, maybe you want to help achieve happiness with code?"
    Thank you, and see [:material-github: issues](https://github.com/iolanta-tech/iolanta/issues)!
