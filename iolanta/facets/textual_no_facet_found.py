from pathlib import Path

import funcy
from rich.markdown import Markdown
from textual.containers import Vertical
from yarl import URL

from iolanta import Facet
from iolanta.facets.page_title import PageTitle
from iolanta.widgets.description import Description

TEXT = """
**😕 Iolanta is unable to visualize this resource**

* The reference type ({reference_type}) might be incorrect;
* The URI might be incorrect;
* Or, no edges might exist which involve it;
* Or maybe Iolanta does not know of such edges.
{content}
{subgraphs}
**What can you do?**

* If you feel this might indicate a bug 🐛, please do let us know at GitHub
issues: https://github.com/iolanta.tech/iolanta/issues
"""

PARSE_ERROR_TEMPLATE = """
**Parse error**

```
{message}
```
"""

CONTENT_TEMPLATE = """
**File content**

```{type}
{content}
```
"""

SUBGRAPHS_TEMPLATE = """
**Subgraphs**

{formatted_subgraphs}
"""


class TextualNoFacetFound(Facet):
    """Facet to handle the case when no facet is found."""

    @property
    def raw_content(self):
        """Content of the file, if applicable."""
        url = URL(self.this)
        if url.scheme != "file":
            return None

        path = Path(url.path)
        if not path.is_relative_to(self.iolanta.project_root):
            return None

        if not path.exists():
            return None

        if path.is_dir():
            return None

        parse_error_msg = self._parse_error_message()
        file_content = path.read_text()
        content = CONTENT_TEMPLATE.format(
            content=file_content,
            type={
                ".yamlld": "yaml",
                ".jsonld": "json",
                ".ttl": "turtle",
            }.get(path.suffix, ""),
        )
        if parse_error_msg:
            content = PARSE_ERROR_TEMPLATE.format(message=parse_error_msg) + content
        return content

    def _parse_error_message(self) -> str | None:
        """Return parse error message for this node if it failed to load."""
        rows = self.query(
            """
            SELECT ?msg WHERE {
                GRAPH <iolanta://_meta> { $this iolanta:parse-error ?msg }
            }
            """,
            this=self.this,
        )
        if row := funcy.first(rows):
            return str(row["msg"])
        return None

    @property
    def subgraphs_description(self) -> str:
        """Return a formatted description of subgraphs, if any exist."""
        rows = self.query(
            "SELECT ?subgraph WHERE { $this iolanta:has-sub-graph ?subgraph }",
            this=self.this,
        )
        subgraphs = funcy.lpluck("subgraph", rows)
        if subgraphs:
            return SUBGRAPHS_TEMPLATE.format(
                formatted_subgraphs="\n".join(
                    [f"- {subgraph}" for subgraph in subgraphs]
                ),
            )

        return ""

    def show(self):
        """Compose the page."""
        return Vertical(
            PageTitle(self.this),
            Description(
                Markdown(
                    TEXT.format(
                        content=self.raw_content or "",
                        subgraphs=self.subgraphs_description or "",
                        reference_type=type(self.this).__name__,
                    ),
                ),
            ),
        )
