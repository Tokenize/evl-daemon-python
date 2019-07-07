import json
import logging

import evl.command as cmd
import evl.event as ev
import evl.tasks.silentarm as silentarm

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
                    "command": o.command.describe(),
                },
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
    def __init__(
        self,
        name: str,
        port: int,
        auth_token: str,
        event_manager: ev.EventManager,
        storage: str = "",
    ):
        self.name = name
        self.port = port
        self.auth_token = auth_token
        self.event_manager = event_manager
        self.storage = storage
        self.current_tasks = {}

    def __str__(self):
        return self.name

    async def handler(self, request: web.Request) -> web.Response:
        """
        Handles incoming web request and routes to appropriate method.
        :param request: Web request
        :return: Web response from method handling the request
        """
        path = request.path
        method = request.method

        if request.query.get("auth_token", "") != self.auth_token:
            logger.debug(
                "Unauthorized attempt to access path: {path}".format(path=path)
            )
            return web.Response(text="Unauthorized.", status=403)

        logger.debug("Request for path: {path}".format(path=path))
        if path == "/events" and method == "GET":
            return self._events()
        elif path == "/status_report" and method == "GET":
            return self._status_report()
        elif path == "/tasks" and (method == "POST" or method == "DELETE"):
            task = await request.json()
            if "type" not in task:
                return web.Response(status=400)

            if method == "POST":
                return self._create_task(task)
            else:
                return self._delete_task(task)
        else:
            return web.Response(text="Not found.", status=404)

    def _events(self) -> web.Response:
        """
        Returns a JSON representation of past events.
        :returns: Web response with JSON representation of past events
        """
        storage = self.event_manager.storage.get(self.storage, None)

        events = []
        if storage is not None:
            events = storage.all()

        content = json.dumps(events, cls=EvlJsonSerializer)
        return web.Response(text=content, content_type="application/json")

    def _create_task(self, task: dict) -> web.Response:
        """
        Creates the task defined in the given dictionary.
        :param task: Dictionary containing task details
        :returns: Web response with result of creating the given task
        """
        if task["type"] == "silent_arm":
            return self._create_silent_arm(task)
        return web.Response(status=400)

    def _create_silent_arm(self, task: dict) -> web.Response:
        """
        Creates a silent alarm task with the given task details.
        :param: Silent alarm task details
        :returns: Web response with result of creating silent alarm task
        """
        if self.current_tasks.get("silent-arm", None):
            return web.Response(status=400)

        zones = task.get("zones", [])
        partitions = task.get("partitions", [])

        silent_arm_task = silentarm.SilentArmTask(self.event_manager, partitions, zones)
        self.current_tasks["silent-arm"] = silent_arm_task
        silent_arm_task.start()

        return web.Response(
            text="silent-arm task created", content_type="application/json"
        )

    def _delete_task(self, task: dict) -> web.Response:
        """
        Deletes the given task, if it exists.
        :param task: Details of task to delete
        :returns: Web response with result of deleting the given task
        """
        if task["type"] == "silent_arm":
            silent_arm = self.current_tasks.get("silent-arm", None)
            if not silent_arm:
                return web.Response(status=400)
            silent_arm.stop()
            del self.current_tasks["silent-arm"]
            return web.Response(text="silent-arm task deleted")
        else:
            return web.Response(status=400)

    def _status_report(self) -> web.Response:
        """
        Returns a JSON representation of the current system status.
        :returns: Web response with JSON representation of current system status
        """
        status = self.event_manager.status_report()
        content = json.dumps(status, cls=EvlJsonSerializer)
        return web.Response(text=content, content_type="application/json")

    async def listen(self) -> None:
        """Starts the HTTP listener."""
        logger.debug("Starting HTTP listener...")
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
