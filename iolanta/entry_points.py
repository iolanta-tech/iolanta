import sys
from typing import List, Type, TypeVar

PluginClass = TypeVar('PluginClass')


if sys.version_info < (3, 10):    # pragma: no cover
    from importlib_metadata import entry_points
else:    # pragma: no cover
    from importlib.metadata import entry_points


def plugins(group_name: str) -> List[PluginClass]:
    """List of plugin classes by group name."""
    return [
        entry_point.load()  # type: ignore
        for entry_point in entry_points(group=group_name)  # type: ignore
    ]
