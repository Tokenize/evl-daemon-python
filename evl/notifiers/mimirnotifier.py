import aiohttp
import json
import logging
import time

from evl.command import Priority
from evl.event import Event

logger = logging.getLogger(__name__)


class MimirNotifier:
    def __init__(
        self,
        url: str,
        uuid: str,
        auth_token: str,
        priority: Priority = Priority.LOW,
        layout: str = None,
        name: str = None,
    ):
        self.priority = priority
        self.url = url
        self.auth_token = auth_token
        self.uuid = uuid
        self.priority = priority
        self.layout = layout
        self.name = name

        if layout is None:
            self.layout = "[{timestamp}]: [{priority}] {event}"

        if name is None:
            self.name = "Mimir Notifier"

        self.session = None

    def __str__(self):
        return self.name

    async def notify(self, event: Event):
        session = self._session()
        try:
            await self._send(session, event)
        except aiohttp.ClientError as e:
            logger.error(f"Error notifying on {self.name}: {e}")

    def _body(self, event: Event):
        utctime = time.gmtime(event.timestamp)
        description = self.layout.format(
            timestamp=event.timestamp_str(), priority=event.priority, event=event
        )
        body = {
            "auth_token": self.auth_token,
            "device": self.uuid,
            "event": {
                "command": event.command.describe(),
                "data": event.describe_data(),
                "zone": event.zone_name(),
                "partition": event.partition_name(),
                "priority": event.priority.name,
                "description": description,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", utctime),
            },
        }
        return json.dumps(body)

    async def _send(self, session: aiohttp.ClientSession, event: Event):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        body = self._body(event)
        async with session.post(self.url, data=body, headers=headers) as resp:
            resp.raise_for_status()

    def _session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            logger.debug("No session available, creating a new one!")
            self.session = aiohttp.ClientSession()
        return self.session
