class ConsoleNotifier():
    def __init__(self, format_str=""):
        self.format_str = format_str
        if len(self.format_str) == 0:
            self.format_str = "Event: {event}"

    def notify(self, event):
        print(self.format_str.format(event=event))
