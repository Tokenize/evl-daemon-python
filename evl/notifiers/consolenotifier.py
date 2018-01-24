from time import localtime, strftime

from evl.command import Priority
from evl.event import Event


class ConsoleNotifier:
    def __init__(self, priority: Priority=Priority.LOW, layout: str=None, name: str=None):
        self.priority = priority
        self.layout = layout
        self.name = name

        if layout is None:
            self.layout = "[{timestamp}] [{priority}] {event}"

        if name is None:
            self.name = "Console Notifier"

        self.time_format = '%Y-%m-%d %H:%M:%S'

    def __str__(self):
        return self.name

    def notify(self, event: Event):
        timestamp = strftime(self.time_format, localtime(event.timestamp))

        if event.priority.value >= self.priority.value:
            print(self.layout.format(timestamp=timestamp, event=event,
                                     priority=event.priority))
