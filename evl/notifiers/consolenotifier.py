from evl.command import Priority
from evl.event import Event


class ConsoleNotifier:
    def __init__(
        self, priority: Priority = Priority.LOW, layout: str = None, name: str = None
    ):
        self.priority = priority
        self.layout = layout
        self.name = name

        if layout is None:
            self.layout = "[{timestamp}] [{priority}] {event}"

        if name is None:
            self.name = "Console Notifier"

    def __str__(self):
        return self.name

    async def notify(self, event: Event):
        if event.priority.value >= self.priority.value:
            print(
                self.layout.format(
                    timestamp=event.timestamp_str(),
                    event=event,
                    priority=event.priority,
                )
            )
