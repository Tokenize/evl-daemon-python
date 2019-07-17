import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

from evl.command import Priority
from evl.event import Event

logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(
        self,
        api_key: str,
        sender: str,
        recipient: str,
        priority: Priority = Priority.CRITICAL,
        layout: str = None,
        subject: str = None,
        name: str = None,
    ):

        self.api_key = api_key
        self.sender = sender
        self.recipient = recipient
        self.priority = priority
        self.layout = layout
        self.subject = subject
        self.name = name

        if layout is None:
            self.layout = "[{timestamp}]: [{priority}] {event}"

        if subject is None:
            self.subject = "EvlDaemon Alert!"

        if name is None:
            self.name = "Email Notifier"

        self.client = SendGridAPIClient(api_key=self.api_key)

    def __str__(self):
        return self.name

    async def notify(self, event: Event):
        if event.priority.value >= self.priority.value:
            self._send_email(event)

    def _send_email(self, event: Event):
        message = self.layout.format(
            timestamp=event.timestamp_str(), priority=event.priority, event=event
        )
        body = Content(mime_type="text/plain", content=message)
        mail = Mail(
            from_email=self.sender,
            to_emails=self.recipient,
            subject=self.subject,
            plain_text_content=body,
        )
        response = self.client.client.mail.send.post(request_body=mail.get())

        if response.status_code not in (200, 202):
            logger.error(
                "Unable to send email! ({status_code} - {message})".format(
                    status_code=response.status_code, message=response.body
                )
            )
