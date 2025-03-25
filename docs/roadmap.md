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
    nanopub-blog-post("Blog post:<br/><strong>Nanopublishing with Iolanta</strong>")
    
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
    
        nanopub-title("Title states the full URL<br/>instead of a readable title") --> nanopublication-is-not-satisfactory
        click nanopub-title "https://github.com/iolanta-tech/iolanta/issues/270"
        class nanopub-title bug
            
        spec-not-visible("Spec link not visible") --> spec("YAML-LD spec is a URL<br/>not title") --> nanopublication-is-not-satisfactory
        class spec bug
        class spec-not-visible bug
        
        app-title-empty("App title is empty:<br/><code>Iolanta —</code>") --> nanopublication-is-not-satisfactory
    end
    
    nanopublication-is-not-satisfactory --> fip-term-messy("<strong>Knowledge representation language</strong><br/>display is messy") --> nanopub-blog-post
    class fip-term-messy bug
    
    python-yaml-ld-markdown-ld("➕ Markdown-LD parser<br/>@ <code>python-yaml-ld</code>") --> markdown-ld("Edit a Markdown-LD document") --> nanopub-blog-post
    click markdown-ld "https://github.com/iolanta-tech/iolanta/issues/261"
        
    classDef bug fill:#f96,color:#f00,stroke:#f00,stroke-width:1px;
```

Want to contribute? Thank you, and see [:material-github: issues](https://github.com/iolanta-tech/iolanta/issues)!