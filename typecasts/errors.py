import typing
from dataclasses import dataclass
from functools import cached_property

from documented import DocumentedError

if typing.TYPE_CHECKING:
    # This is to avoid circular imports in the form of
    #     typecasts.errors ⇆ typecasts.main
    from typecasts.main import Typecasts


@dataclass
class RedundantIdentity(DocumentedError):
    """
    Attempted to register redundant identity function.

    At {self.typecasts}, it has been attempted to register a cast function to
    convert {self.idempotent_type} to itself, which does not make sense.

    `typecasts` will automatically use an identity function for such
    conversions.
    """

    typecasts: 'Typecasts'
    idempotent_type: type


@dataclass
class TypecastNotFound(DocumentedError):
    """
    A method to cast one type to another was not found.

    Attempted to cast

        from: {self.source_type}
        to:   {self.destination_type}

    Assuming you are using `DefaultTypecasts`,

    [HINT] You may create such a function as follows:

        DefaultTypecasts[{self.source_name}, {self.destination_name}] = ...

    [HINT] Or, using decorator syntax:

    @DefaultTypecasts.register({self.source_name}, {self.destination_name})
    def cast_{self.source_name_lower}_to_{self.destination_name_lower}(
        source_value: {self.source_name},
    ) -> {self.destination_name}:
        return ...

    For further details, see:

        - Examples at typecasts.defaults module
        - Or docs at https://pyplatonic.dev/typecasts/
    """

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

    @property
    def source_name_lower(self):
        return self.source_name.lower()

    @property
    def destination_name_lower(self):
        return self.destination_name.lower()
