import logging

import evl.event as ev

from aiohttp import web
import jsonpickle

logger = logging.getLogger(__name__)


class AsyncHttpListener:

    def __init__(self, name: str, port: int, auth_token: str,
                 event_manager: ev.EventManager, storage: str = ""):
        self.name = name
        self.port = port
        self.auth_token = auth_token
        self.event_manager = event_manager
        self.storage = storage

    def __str__(self):
        return self.name

    async def handler(self, request: web.Request) -> web.Response:
        path = request.path

        if request.query.get("auth_token", "") != self.auth_token:
            logger.debug("Unauthorized attempt to access path: {path}".format(path=path))
            return web.Response(text="Unauthorized.", status=403)

        logger.debug("Request for path: {path}".format(path=path))
        if path == "/status_report":
            return web.Response(text=self._status_report(), content_type="application/json")
        else:
            return web.Response(text="Not found.", status=404)

    def _status_report(self) -> str:
        status = self.event_manager.status_report()
        return jsonpickle.encode(status, unpicklable=True)

    async def listen(self) -> None:
        logger.debug("Starting HTTP listener...")
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
