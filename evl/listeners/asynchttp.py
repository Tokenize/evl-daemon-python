import json
import logging

import evl.command as cmd
import evl.event as ev

from aiohttp import web

logger = logging.getLogger(__name__)


class EvlJsonSerializer(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ev.Event):
            event_json = {
                "command": o.command.number,
                "data": o.data,
                "zone": o.zone,
                "partition": o.partition,
                "priority": o.priority.name,
                "timestamp": o.timestamp,
                "description": {
                    "data": o.describe_data(),
                    "command": o.command.describe()
                }
            }
            return event_json
        elif isinstance(o, cmd.Command):
            return o.describe()
        elif isinstance(o, cmd.CommandType):
            return o.name
        elif isinstance(o, cmd.Priority):
            return o.name

        return json.JSONEncoder.default(self, o)


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
        elif path == "/events":
            return self._events()
        else:
            return web.Response(text="Not found.", status=404)

    def _events(self) -> web.Response:
        storage = self.event_manager.storage.get(self.storage, None)
        if storage:
            events = storage.all()
        else:
            events = []

        content = json.dumps(events, cls=EvlJsonSerializer)
        return web.Response(text=content, content_type="application/json")

    def _status_report(self) -> str:
        status = self.event_manager.status_report()
        return json.dumps(status, cls=EvlJsonSerializer)

    async def listen(self) -> None:
        logger.debug("Starting HTTP listener...")
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
