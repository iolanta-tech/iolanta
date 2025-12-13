from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP

from iolanta.cli.main import render_and_return

mcp = FastMCP("Iolanta MCP Server")


@mcp.tool()
def render_uri(
    uri: Annotated[str, 'URL, or file system path, to render'],
    as_format: Annotated[str, 'Format to render as. Examples: `labeled-triple-set`, `mermaid`'],
) -> str:
    """Render a URI."""
    result = render_and_return(uri, as_format)
    return str(result)


@mcp.prompt(description="How to author Linked Data with Iolanta")
def ld_authoring_rules() -> str:
    """How to author Linked Data with Iolanta."""
    rules_path = Path(__file__).parent / 'prompts' / 'rules.md'
    return rules_path.read_text()


@mcp.prompt(description="How to author nanopublication assertions with Iolanta")
def nanopublication_assertion_authoring_rules() -> str:
    """How to author nanopublication assertions with Iolanta."""
    rules_path = Path(__file__).parent / 'prompts' / 'nanopublication_assertion_authoring_rules.md'
    return rules_path.read_text()


def app():
    mcp.run()


if __name__ == "__main__":
    app()
