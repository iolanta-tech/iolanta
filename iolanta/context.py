from copy import deepcopy

from deepmerge import always_merger

from mkdocs_iolanta.types import Context


def merge(first: Context, second: Context) -> Context:
    """
    Merge two contexts into one.

    Second context can override the first.
    """
    if isinstance(second, list):
        return [
            merge(first, sub_second)
            for sub_second in second
        ]

    return deepcopy(
        always_merger.merge(
            base=first,
            nxt=second,
        ),
    )
