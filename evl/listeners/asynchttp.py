import evl.event as ev

from aiohttp import web


class AsyncHttpListener:

    def __init__(self, name: str, port: int, auth_token: str,
                 event_manager: ev.EventManager, storage: str = ""):
        self.name = name
        self.port = port
        self.auth_token = auth_token
        self.event_manager = event_manager
        self.storage = storage

    async def handler(self, request: web.Request) -> web.Response:
        if request.query.get("auth_token", "") != self.auth_token:
            return web.Response(text="Unauthorized.", status=403)

        return web.Response(text="OK")

    async def listen(self) -> None:
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
