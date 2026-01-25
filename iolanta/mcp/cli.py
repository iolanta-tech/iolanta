from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from rdflib import URIRef
from yarl import URL

from iolanta.cli.main import render_and_return

mcp = FastMCP("Iolanta MCP Server")


@mcp.tool()
def render_uri(
    uri: Annotated[str, "URL, or file system path, to render"],
    as_format: Annotated[
        str, "Format to render as. Examples: `labeled-triple-set`, `mermaid`"
    ],
) -> str:
    """Render a URI."""
    # Parse string URL to URIRef
    node_url = URL(uri)
    if node_url.scheme and node_url.scheme != "file":
        node = URIRef(uri)
    else:
        path = Path(node_url.path).absolute()
        node = URIRef(f"file://{path}")

    return str(render_and_return(node=node, as_datatype=as_format))


def app():
    mcp.run()


if __name__ == "__main__":
    app()
