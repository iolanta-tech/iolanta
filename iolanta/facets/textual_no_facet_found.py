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

* The URI might be incorrect;
* Or, no edges might exist which involve it;
* Or maybe Iolanta does not know of such edges.
{content}
{subgraphs}
**What can you do?**

* If you feel this might indicate a bug 🐛, please do let us know at GitHub
issues: https://github.com/iolanta.tech/iolanta/issues
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
        url = URL(self.uriref)
        if url.scheme != 'file':
            return None

        path = Path(url.path)
        if not path.is_relative_to(self.iolanta.project_root):
            return None

        if not path.exists():
            return None

        if path.is_dir():
            return None

        file_content = path.read_text()
        return CONTENT_TEMPLATE.format(
            content=file_content,
            type={
                '.yamlld': 'yaml',
                '.jsonld': 'json',
            }.get(path.suffix, ''),
        )

    @property
    def subgraphs_description(self) -> str:
        """Return a formatted description of subgraphs, if any exist."""
        rows = self.query(
            'SELECT ?subgraph WHERE { $this iolanta:has-sub-graph ?subgraph }',
            this=self.this,
        )
        subgraphs = funcy.lpluck('subgraph', rows)
        if subgraphs:
            return SUBGRAPHS_TEMPLATE.format(
                formatted_subgraphs='\n'.join([
                    f'- {subgraph}'
                    for subgraph in subgraphs
                ]),
            )

        return ''

    def show(self):
        """Compose the page."""
        return Vertical(
            PageTitle(self.this),
            Description(
                Markdown(
                    TEXT.format(
                        content=self.raw_content or '',
                        subgraphs=self.subgraphs_description or '',
                    ),
                ),
            ),
        )
