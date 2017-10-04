from time import localtime, strftime

from sendgrid import Email, SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

from evl.event import Event, Priority


class EmailNotifier:
    def __init__(self, api_key: str, sender: str, recipient: str,
                 priority: Priority=Priority.CRITICAL, layout: str=None, subject: str=None):
        self.api_key = api_key
        self.sender = Email(sender)
        self.recipient = Email(recipient)
        self.priority = priority
        self.layout = layout
        self.subject = subject

        if layout is None:
            self.layout = "[{timestamp}]: [{priority}] {event}"

        if subject is None:
            self.subject = "EvlDaemon Alert!"

        self.client = SendGridAPIClient(apikey=self.api_key)
        self.timestamp_format = '%Y-%m-%d %H:%M:%S'

    def notify(self, event: Event):
        timestamp = strftime(self.timestamp_format, localtime(event.timestamp))

        if event.priority.value >= self.priority.value:
            self._send_email(event, timestamp)

    def _send_email(self, event: Event, timestamp):
        message = self.layout.format(timestamp=timestamp, priority=event.priority, event=event)
        body = Content(type_="text/plain", value=message)
        mail = Mail(self.sender, self.subject, self.recipient, body)
        response = self.client.client.mail.send.post(request_body=mail.get())

        if response.status_code != "200":
            print("ERROR: Unable to send email! ({status_code} - {message})".format(status_code=response.status_code,
                                                                                    message=response.body))
