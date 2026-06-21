# Jeeves

## Development server

**D00.** To run the MkDocs development server, use `j serve`. The server runs on `http://localhost:6451`. Normally, the user already has it running for development.

**D01.** The `j serve` command runs `mkdocs serve -a localhost:6451` (note: the docstring incorrectly states port 9841, but the actual port is 6451).

## Adding Jeeves Commands

**J00.** Jeeves is a task runner based on Typer. To add a new development command, add a function to `jeeves/__init__.py`. Functions in this module automatically become commands accessible via `j <command-name>`.

**J01.** Function names use underscores (e.g., `def my_command()`), but are invoked with dashes: `j my-command` (Typer automatically converts underscores to dashes).

**J02.** Commands should:
- Have a docstring describing what they do (shown in `j --help`)
- Use the `sh` library for shell commands (e.g., `sh.mkdocs.serve(...)`)
- Use `console` from Rich for colored output (e.g., `console.print("[green]Success[/green]")`)
- Accept parameters as function arguments (Typer automatically creates CLI arguments)

**J03.** Example command:
```python
def build_docs():
    """Build documentation and deploy to GitHub Pages."""
    sh.mkdocs('gh-deploy', '--force', '--clean')
    console.print("[green]✅ Documentation deployed[/green]")
```

**J04.** For commands that wrap existing tools, prefer composing standard commands with pipes/redirection rather than creating a Jeeves command. Only create Jeeves commands when they add significant value (e.g., complex workflows, multiple steps, or project-specific logic).

**J06.** MkDocs snippet-included Mermaid diagrams (`.mmd` files pulled in via `--8<--`) are registered in `DOCS_MERMAID_ARTIFACTS` in `jeeves/__init__.py`. Regenerate them with `j generate-docs-mermaid`. When adding a new snippet-included diagram, add its source/target pair to that registry.

**J07.** `j generate-remote-contexts-considered-harmful-artifacts` regenerates pyld tab outputs for that blog post only. Mermaid for that post is covered by `j generate-docs-mermaid`.
