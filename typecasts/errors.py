from dataclasses import dataclass
from functools import cached_property

import typing

if typing.TYPE_CHECKING:
    from typecasts.main import Typecasts


@dataclass
class RedundantIdentity(Exception):
    typecasts: 'Typecasts'
    idempotent_type: type

    def __str__(self):
        return (
            f'An attempt has been made to register a cast function at '
            f'{self.typecasts} converting values of {self.idempotent_type} '
            f'into itself. This is redundant because a natural such conversion '
            f'is identity function.'
        )


@dataclass
class TypecastNotFound(Exception):
    """A method to cast one type to another was not found."""
    source_type: type
    destination_type: type
    typecasts: 'Typecasts'

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
            f'    def cast_{self.source_name.lower()}_to_'
            f'{self.destination_name.lower()}('
            f'source_value: {self.source_name}) -> '
            f'{self.destination_name}:\n'
            f'        return ...\n'
            f'\n'
            f'Or, see docs for details: https://platonic.io/typecasts/'
        )
