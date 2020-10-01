from typing import (
    TypeVar, Callable, Dict, Tuple, Any, Type,
)

from typecasts.errors import RedundantIdentity, TypecastNotFound
from typecasts.identity import identity

SourceType = TypeVar('SourceType')
DestinationType = TypeVar('DestinationType')

TypePair = Tuple[Type[SourceType], Type[DestinationType]]
Cast = Callable[[SourceType], DestinationType]


class Typecasts(Dict[Tuple[type, type], Callable[[Any], Any]]):
    def __getitem__(
        self,
        type_pair: Tuple[Type[SourceType], Type[DestinationType]],
    ) -> Callable[[SourceType], DestinationType]:
        source_type, destination_type = type_pair

        if source_type == destination_type:
            return identity  # type: ignore

        try:
            return super().__getitem__(type_pair)

        except KeyError as err:
            # FIXME This seems to violate Liskov substitution principle.
            #   Shall we remove the inheritance from Dict?
            raise TypecastNotFound(
                source_type=source_type,
                destination_type=destination_type,
                typecasts=self,
            ) from err

    def __setitem__(
        self,
        type_pair: Tuple[Type[SourceType], Type[DestinationType]],
        cast: Callable[[SourceType], DestinationType],
    ) -> None:
        source_type, destination_type = type_pair

        if source_type == destination_type:
            raise RedundantIdentity(
                idempotent_type=source_type,
                typecasts=self,
            )

        return super().__setitem__(type_pair, cast)

    def register(
        self,
        source_type: Type[SourceType],
        destination_type: Type[DestinationType],
    ):
        """Decorator to register a function as a typecast."""
        def registrar(function: Callable[[SourceType], DestinationType]):
            self[source_type, destination_type] = function
            return function

        return registrar
