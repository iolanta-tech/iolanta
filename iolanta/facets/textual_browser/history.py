from collections import deque
from dataclasses import dataclass, field
from typing import Generic, TypeVar

LocationType = TypeVar('LocationType')


@dataclass
class BrowserHistory(Generic[LocationType]):
    history: deque = field(default_factory=deque)
    current: str | None = None
    forward_stack: deque = field(default_factory=deque)

    def visit(self, url: str):
        if self.current is not None:
            self.history.append(self.current)
        self.current = url
        self.forward_stack.clear()

    def back(self):
        if self.history:
            self.forward_stack.appendleft(self.current)
            self.current = self.history.pop()
        else:
            print("No history to go back to.")

    def forward(self):
        if self.forward_stack:
            self.history.append(self.current)
            self.current = self.forward_stack.popleft()
        else:
            print("No forward history to go to.")

    def goto(self, url: str):
        if self.current is not None:
            self.history.append(self.current)
        self.current = url
        self.forward_stack.clear()
