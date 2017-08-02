class EventManager():

    def __init__(self, event_queue, notifiers=None):
        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers
        self._event_queue = event_queue

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def wait(self):
        while True:
            event = self._event_queue.get()
            for notifier in self._notifiers:
                notifier.notify(event)
