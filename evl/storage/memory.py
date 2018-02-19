from collections import deque

from evl.event import Event


class MemoryStorage:
    def __init__(self, size=100, name='Memory'):
        self.size = size
        self.name = name
        self._deque = deque(maxlen=self.size)

    def store(self, event: Event):
        self._deque.append(event)

    def all(self):
        return self._deque

    def __str__(self):
        return "{name}".format(name=self.name)
