from dataclasses import dataclass
from functools import cached_property, partial
from typing import (
    TypeVar, Callable, Dict, Tuple, Any,
)

from typecasts.identity import identity

SourceType = TypeVar('SourceType')
DestinationType = TypeVar('DestinationType')

TypePair = Tuple[type, type]


class Typecasts(Dict[Tuple[type, type], Callable[[Any], Any]]):
    def __getitem__(self, type_pair: TypePair) -> Callable[[Any], Any]:
        source_type, destination_type = type_pair

        if source_type == destination_type:
            return identity

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


DefaultTypecasts = Typecasts()


# Basic, primitive casts
DefaultTypecasts.update({
    (int, float): float,
    (int, bytes): bytes,
})

# String to bytes and vice versa
DefaultTypecasts.update({
    (bytes, str): partial(bytes.decode, encoding='utf-8'),
    (str, bytes): str.encode,
})


@dataclass
class TypecastNotFound(Exception):
    """A method to cast one type to another was not found."""
    source_type: type
    destination_type: type
    typecasts: Typecasts

    @cached_property
    def source_name(self):
        return self.source_type.__name__

    @cached_property
    def destination_name(self):
        return self.destination_type.__name__

    @cached_property
    def typecasts_name(self):
        return self.typecasts.__class__.__name__

    def __str__(self):
        return (
            f'{self.typecasts} typecasts repository does not have a function '
            f'to cast {self.source_type} values to {self.destination_type}.\n'
            f'\n'
            f'[HINT] You may create such a function as follows:\n'
            f'\n'
            f'    {self.typecasts_name}'
            f'[{self.source_name}, {self.destination_name}]'
            f' = {self.destination_name}\n'
            f'\n'
            f'[HINT] Or, using decorator syntax:\n'
            f'\n'
            f'    @{self.typecasts_name}.register({self.source_name}, '
            f'{self.destination_name})\n'
            f'    def cast_{self.source_name}_to_'
            f'{self.destination_name}(source_value: {self.source_name}) -> '
            f'{self.destination_name}:\n'
            f'        return ...\n'
            f'\n'
            f'Or, see docs for details: https://platonic.io/typecasts/'
        )
