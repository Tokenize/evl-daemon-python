from time import localtime, strftime

from evl.event import Event, Priority


class ConsoleNotifier:
    def __init__(self, priority: Priority=Priority.LOW, layout: str=None):
        self.priority = priority
        self.layout = layout
        if layout is None:
            self.layout = "[{timestamp}] [{priority}] {event}"

        self.time_format = '%Y-%m-%d %H:%M:%S'

    def notify(self, event: Event):
        timestamp = strftime(self.time_format, localtime(event.timestamp))

        if event.priority.value >= self.priority.value:
            print(self.layout.format(timestamp=timestamp, event=event,
                                     priority=event.priority))
