---
date: 2024-11-15
title: Page for the title datatype is in Markdown with Script tag
---

# Page for the `title` datatype is in Markdown with `script` tag

## Context

I need the https://iolanta.tech/datatypes/title datatype page to expose LD data about the datatype it stands for:

* `rdfs:subClassOf`,
* `rdfs:label`,
* `rdfs:description`,

and such. I can achieve that by:

* Adding a `Link` HTTP header,
* Adding a `Link` meta tag,
* Or embedding the JSON/YAML-LD into a `<script>` tag on the page.

3rd option sounds easiest, that is what I will in fact do.

Now, how can I do it?

* Write it manually into the page content
* Generate it from the front matter somehow
* Generate it from a standalone YAML-LD file

## Decision

I'll do it manually for the time being.

## Consequences

We'll automate this later if we survive.
