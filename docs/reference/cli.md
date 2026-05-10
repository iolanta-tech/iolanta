---
title: Command line interface
hide: [toc]
---

# Command line interface

The `iolanta` command renders Linked Data resources from local files, URLs,
queries, search results, and Jinja2 Markdown templates.

Use one input mode at a time:

- a positional URL or file path,
- `--query`,
- `--search`,
- `--render-template`.

## Reference

::: mkdocs-typer2
    :module: iolanta.cli
    :name: iolanta
    :pretty: true
    :engine: native

## Common modes

Render a URL or local file as an output datatype:

```shell
iolanta https://orcid.org/0000-0002-1825-0097 --as title
```

Run a SPARQL query and render the result:

```shell
iolanta --query 'SELECT * WHERE { ?s ?p ?o } LIMIT 10' --as table
```

Search Linked Data APIs and emit JSON Lines:

```shell
iolanta --search 'Isaac Asimov' --as jsonl
```

Pre-render a Jinja2 Markdown document and redirect the rendered Markdown to a
file:

```shell
iolanta --render-template source.jinja2.md > source.output.md
```

## Template rendering

`--render-template` prints rendered Markdown to stdout. Use shell redirection to
write the output to a file.

Template rendering uses the template file's parent directory as
`Iolanta.project_root`. Templates can use local YAML-LD files in that directory,
project data, installed Iolanta facilities, and normal web loading.

See [`--render-template` macros & variables](/reference/render-template-macros-and-variables/)
for the supported template surface.
