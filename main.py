import functools
import json
from pathlib import Path
from typing import Any  # noqa: WPS202

import yaml_ld
from mkdocs_macros.plugin import MacrosPlugin
from rdflib import URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def as_uri(uri: Any) -> URIRef:
    """Convert a path, string, or URIRef to a URIRef."""
    match uri:
        case Path() as path:
            return path_to_iri(path)
        case URIRef() as uriref:
            return uriref
        case str() as uri_string:
            return URIRef(uri_string)

    uri_type = type(uri)
    raise NotImplementedError(f"{uri} ({uri_type.__name__}) is unknown")


def resolve_datatype_uri(uri: str) -> URIRef:
    """Resolve a datatype URI string to a URIRef."""
    # If it's already a full URI, return it directly
    if uri.startswith("http://") or uri.startswith("https://"):
        return URIRef(uri)
    # Otherwise, treat it as a short key in the DATATYPES namespace
    return DATATYPES[uri]


def sparql_query_from_file(iolanta: Iolanta, sparql_file_path: Path, **kwargs) -> str:  # noqa: WPS210
    """Execute SPARQL query from file with optional parameters and return results as markdown table."""
    query_text = sparql_file_path.read_text()
    query_results = iolanta.query(query_text, **kwargs)

    # Handle ASK queries returning a boolean
    if isinstance(query_results, bool):
        return "✅ `True`" if query_results else "❌ `False`"

    if not query_results:
        return "_No results_"

    # Get column headers from first row
    first_row = query_results[0]
    headers = list(first_row.keys())

    # Build markdown table
    table_lines = _build_markdown_table(query_results, headers)
    return "\n".join(table_lines)


def _format_cell(cell_value: object) -> str:
    """Format a cell for Markdown table: wrap in backticks and escape backticks inside."""
    cell_string = str(cell_value)
    cell_string = cell_string.replace("`", r"\`")
    return f"`{cell_string}`"


def _build_markdown_table(query_results, headers):  # noqa: WPS210
    """Build markdown table from query results."""
    table_lines = []
    header_parts = ["| "] + headers + [" |"]
    header_row = " ".join(header_parts)
    table_lines.append(header_row)
    
    separator_count = len(headers)
    separator_parts = ["---" for _ in range(separator_count)]
    separator_row_parts = ["| "] + separator_parts + [" |"]
    separator_row = " ".join(separator_row_parts)
    table_lines.append(separator_row)

    for row in query_results:
        row_values = [_format_cell(row.get(header, "")) for header in headers]
        data_row_parts = ["| "] + row_values + [" |"]
        data_row = " ".join(data_row_parts)
        table_lines.append(data_row)

    return table_lines


def on_post_page_macros(env):
    """
    Actions to be done after macro interpretation,
    when the macros have been rendered
    This will add a (Markdown or HTML) footer -- produced by Python.
    """

    ld = yaml_ld.expand(env.page.file.abs_src_path)
    serialized_ld = json.dumps(ld, indent=2, default=str)
    snippet = f'<script type="application/ld+json">\n{serialized_ld}\n</script>'

    env.markdown = f"{env.markdown}\n{snippet}"


def _as_filter(iolanta_instance: Iolanta, uri: str, datatype: str) -> str:
    """Convert URI to specified datatype."""
    return iolanta_instance.render(
        node=as_uri(uri),
        as_datatype=resolve_datatype_uri(datatype),
    )


def define_env(env: MacrosPlugin):
    iolanta = Iolanta(project_root=Path(__file__).parent / "docs")

    env.filters["as"] = functools.partial(_as_filter, iolanta)
    env.filters["uri"] = as_uri
    env.macros["sparql"] = functools.partial(sparql_query_from_file, iolanta)
    env.macros["path_to_uri"] = path_to_iri
    env.variables["docs"] = Path(__file__).parent / "docs"
    env.variables["iolanta"] = Path(__file__).parent
    env.variables["URIRef"] = URIRef
