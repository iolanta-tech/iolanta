---
title: Roadmap
hide:
    - toc
    - navigation
---

# :octicons-project-roadmap-24: Roadmap

Roadmap of Iolanta development shows known yet unsolved bugs and to-do items. Some of them are clickable: they already have their GitHub issues associated to them.

```mermaid
graph LR
    nanopub-blog-post("Blog post:<br/><strong>Nanopublishing with Iolanta</strong>") --> markdown-nanopub-blog-post("Blog post:<br/><strong>Quick & readable Nanopublications with Markdown-LD")
    
    nanopub-rs-graph("Publish an assertion from file<br/>@ <code>nanopub-rs</code>") --> nanopub-yaml-ld("Publish a YAML-LD assertion<br/>@ <code>nanopub-rs</code>") --> nanopub-blog-post
    
    subgraph "YAML-LD nanopublication on the front page"
        direction LR
        nanopublication-is-not-satisfactory("Nanopublication on front page<br/>is not satisfactory")
        class nanopublication-is-not-satisfactory bug
        
        literal-clickable("YAML-LD literal is clickable") --> nanopublication-is-not-satisfactory
        click literal-clickable "https://github.com/iolanta-tech/iolanta/issues/260"
        class literal-clickable bug
        
        back("'Back' ← link is visible") --> nanopublication-is-not-satisfactory
        class back bug
    
        fwd("'Fwd' → link is visible") --> nanopublication-is-not-satisfactory
        class fwd bug
            
        spec("YAML-LD spec is a URL<br/>not title") --> nanopublication-is-not-satisfactory
        class spec bug
    end
    
    nanopublication-is-not-satisfactory --> fip-term-messy("<strong>Knowledge representation language</strong><br/>display is messy") --> nanopub-blog-post
    class fip-term-messy bug
    
    python-yaml-ld-markdown-ld("➕ Markdown-LD parser<br/>@ <code>python-yaml-ld</code>") --> markdown-ld("Edit a Markdown-LD document") --> markdown-nanopub-blog-post
    click markdown-ld "https://github.com/iolanta-tech/iolanta/issues/261"
        
    classDef bug fill:#f96,color:#f00,stroke:#f00,stroke-width:1px;
```

Want to contribute? Thank you, and see [:material-github: issues](https://github.com/iolanta-tech/iolanta/issues)!