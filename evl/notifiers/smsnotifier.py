from time import localtime, strftime

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from evl.event import Priority, Event


class SmsNotifier:

    def __init__(self, sid: str, auth_token: str, sender: str, recipient: str,
                 priority: Priority=Priority.CRITICAL, layout: str=None):
        self.sid = sid
        self.auth_token = auth_token
        self.sender = sender
        self.recipient = recipient
        self.priority = priority
        self.layout = layout

        if layout is None:
            self.layout = "[{timestamp}]: [{priority}] {event}"

        self.client = Client(sid, auth_token)

        self.timestamp_format = '%Y-%m-%d %H:%M:%S'

    def notify(self, event: Event):
        timestamp = strftime(self.timestamp_format, localtime(event.timestamp))

        if event.priority.value >= self.priority.value:
            self._send_sms(event, timestamp)

    def _send_sms(self, event: Event, timestamp):
        message = self.layout.format(timestamp=timestamp,
                                     priority=event.priority, event=event)

        try:
            self.client.messages.create(self.recipient, body=message, from_=self.sender)
        except TwilioException as e:
            print("ERROR: Unable to send SMS! ({exception})".format(exception=e))
