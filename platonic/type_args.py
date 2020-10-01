from typing import Any, Tuple, get_args, TypeVar, Iterator


def iterate_by_type_parameters(instance: Any) -> Iterator[Tuple[type, ...]]:
    try:
        classes = (instance.__orig_class__, *instance.__orig_bases__)

    except AttributeError:
        classes = instance.__orig_bases__

    for cls in classes:
        yield get_args(cls)


def generic_type_args(instance: Any) -> Tuple[type, ...]:  # type: ignore
    parameters, *etc = iterate_by_type_parameters(instance)
    return parameters
