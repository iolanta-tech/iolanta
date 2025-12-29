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
    return str(render_and_return(uri, as_format))


def app():
    mcp.run()


if __name__ == "__main__":
    app()
