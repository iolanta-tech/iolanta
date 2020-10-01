from typing import Any, Tuple, get_args


def generic_type_args(instance: Any) -> Tuple[type, ...]:  # type: ignore
    for parent in instance.__orig_bases__:  # type: ignore  # noqa: WPS609
        type_args = get_args(parent)
        if type_args:
            return type_args

    return ()
