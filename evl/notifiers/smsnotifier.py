import logging
from time import localtime, strftime

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from evl.command import Priority
from evl.event import Event

logger = logging.getLogger(__name__)


class SmsNotifier:
    def __init__(
        self,
        sid: str,
        auth_token: str,
        sender: str,
        recipient: str,
        priority: Priority = Priority.CRITICAL,
        layout: str = None,
        name: str = None,
    ):

        self.sid = sid
        self.auth_token = auth_token
        self.sender = sender
        self.recipient = recipient
        self.priority = priority
        self.layout = layout
        self.name = name

        if layout is None:
            self.layout = "[{timestamp}]: [{priority}] {event}"

        if name is None:
            self.name = "SMS Notifier"

        self.client = Client(sid, auth_token)

    def __str__(self):
        return self.name

    async def notify(self, event: Event):
        if event.priority.value >= self.priority.value:
            self._send_sms(event)

    def _send_sms(self, event: Event):
        message = self.layout.format(
            timestamp=event.timestamp_str(), priority=event.priority, event=event
        )

        try:
            self.client.messages.create(self.recipient, body=message, from_=self.sender)
        except TwilioException as e:
            logger.error("Unable to send SMS! ({exception})".format(exception=e))
