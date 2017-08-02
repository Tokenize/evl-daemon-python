from datetime import datetime


class ConsoleNotifier:
    def __init__(self, format_str: str=None):
        self.format_str = format_str
        if format_str is None:
            self.format_str = "[{timestamp}] Event: {event}"

    def notify(self, event, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        print(self.format_str.format(timestamp=timestamp, event=event))
