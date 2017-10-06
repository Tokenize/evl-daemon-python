from collections import deque

from evl.event import Event


class MemoryStorage:
    def __init__(self, size=100):
        self.size = size
        self._deque = deque(maxlen=self.size)

    def store(self, event: Event):
        self._deque.append(event)

    def all(self):
        return self._deque
