from collections import deque
from dataclasses import dataclass, field
from typing import Generic, TypeVar

LocationType = TypeVar('LocationType')


@dataclass
class NavigationHistory(Generic[LocationType]):
    """Navigation history."""

    past: deque = field(default_factory=deque)
    current: LocationType | None = None
    future: deque = field(default_factory=deque)

    def goto(self, location: LocationType) -> LocationType:
        """Go to a location."""
        if self.current is not None:
            self.past.append(self.current)
        self.current = location
        self.future.clear()

        return self.current

    def back(self) -> LocationType | None:
        """Go back in history."""
        if self.past:
            self.future.appendleft(self.current)
            self.current = self.past.pop()

        return self.current

    def forward(self) -> LocationType | None:
        """Go forward in history."""
        if self.future:
            self.past.append(self.current)
            self.current = self.future.popleft()

        return self.current
