from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from documented import DocumentedError

from iolanta.models import LDDocument


@dataclass
class NotAContext(DocumentedError):
    """
    This is not a context.

    Document is expected to be a context but it's not.

    It lacks the `@context` key.

    Document: {self.document}

    Path: {self.formatted_path}
    """

    document: LDDocument
    path: Optional[Path] = None

    @property
    def formatted_path(self):
        return self.path or '<Unknown>'


def ensure_is_context(document: LDDocument) -> LDDocument:
    if '@context' not in document:
        raise NotAContext(document=document)

    return document
