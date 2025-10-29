from pathlib import Path

from mkdocs_macros.plugin import MacrosPlugin
from rdflib import URIRef

from iolanta.conversions import path_to_iri
from iolanta.iolanta import Iolanta
from iolanta.namespaces import DATATYPES


def as_uri(uri: Path | str) -> URIRef:
    """Convert a path or string to a URIRef."""
    match uri:
        case Path() as path:
            return path_to_iri(path)

    uri_type = type(uri)
    raise NotImplementedError(f'{uri} ({uri_type.__name__}) is unknown')


def resolve_datatype_uri(uri: str) -> URIRef:
    """Resolve a datatype URI string to a URIRef."""
    return DATATYPES[uri]


def sparql_query_from_file(iolanta: Iolanta, sparql_file_path: Path, **kwargs) -> str:
    """Execute SPARQL query from file with optional parameters and return results as markdown table."""
    query_text = sparql_file_path.read_text()
    results = iolanta.query(query_text, **kwargs)

    # Handle ASK queries returning a boolean
    if isinstance(results, bool):
        return "✅ `True`" if results else "❌ `False`"

    if not results:
        return "_No results_"

    # Get column headers from first row
    first_row = results[0]
    headers = list(first_row.keys())

    def format_cell(value: object) -> str:
        """Format a cell for Markdown table: wrap in backticks and escape backticks inside."""
        s = str(value)
        s = s.replace("`", "\\`")
        return f"`{s}`"

    # Build markdown table
    table_lines = []
    table_lines.append("| " + " | ".join(headers) + " |")
    table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in results:
        values = [format_cell(row.get(h, "")) for h in headers]
        table_lines.append("| " + " | ".join(values) + " |")

    return "\n".join(table_lines)


def define_env(env: MacrosPlugin):
    iolanta = Iolanta(project_root=Path(__file__).parent / 'docs')

    def as_filter(uri: str, datatype: str) -> str:
        """Convert URI to specified datatype."""
        return iolanta.render(
            node=as_uri(uri),
            as_datatype=resolve_datatype_uri(datatype),
        )

    def sparql_macro(file_path: Path, **kwargs) -> str:
        """Execute SPARQL from file with parameters and return markdown table."""
        return sparql_query_from_file(iolanta, file_path, **kwargs)

    env.filters['as'] = as_filter
    env.filters['uri'] = as_uri
    env.macros['sparql'] = sparql_macro
    env.macros['path_to_uri'] = path_to_iri
    env.variables['docs'] = Path(__file__).parent / 'docs'
    env.variables['iolanta'] = Path(__file__).parent
    env.variables['URIRef'] = URIRef
