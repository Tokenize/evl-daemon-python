import datetime

class ConsoleNotifier():
    def __init__(self, format_str=""):
        self.format_str = format_str
        if len(self.format_str) == 0:
            self.format_str = "[{timestamp}] Event: {event}"

    def notify(self, event):
        timestamp = datetime.datetime.now()
        print(self.format_str.format(timestamp=timestamp, event=event))
