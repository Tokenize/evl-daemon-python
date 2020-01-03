import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


class HeartbeatTask:
    def __init__(
        self,
        name: str,
        device_id: int,
        uuid: str,
        interval: int,
        url: str,
        auth_token: str,
    ):
        self.name = name
        self.device_id = device_id
        self.uuid = uuid
        self.interval = int(interval)
        self.url = f"{url}/{device_id}"
        self.auth_token = auth_token

        self.body_content = {"auth_token": self.auth_token, "device": self.uuid}

    def __str__(self):
        return "Heartbeat Task"

    async def start(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            while True:
                logger.debug("Pinging heartbeat server...")
                try:
                    await self._ping(session)
                except aiohttp.ClientError as e:
                    logger.debug(f"Error pinging heartbeat server: {e}")

                await asyncio.sleep(self.interval)

    async def _ping(self, session: aiohttp.ClientSession):
        async with session.put(self.url, json=self.body_content) as resp:
            resp.raise_for_status()
            logger.debug("Successfully pinged heartbeat server.")
