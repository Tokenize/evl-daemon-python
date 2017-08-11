from datetime import datetime


from evl.command import Priority
from evl.event import Event


class ConsoleNotifier:
    def __init__(self, priority: Priority=Priority.LOW, layout: str=None):
        self.priority = priority
        self.layout = layout
        if layout is None:
            self.layout = "[{timestamp}] [{priority}] {event}"

    def notify(self, event: Event, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        if event.priority.value >= self.priority.value:
            print(self.layout.format(timestamp=timestamp, event=event,
                                     priority=event.priority))
