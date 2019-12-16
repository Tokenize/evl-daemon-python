import flask
import gevent.pywsgi as wsgi
import logging

import evl.command as cmd
import evl.event as ev
import evl.tasks.silentarm as silentarm

logger = logging.getLogger(__name__)


class EvlJsonSerializer(flask.json.JSONEncoder):
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

        return flask.json.JSONEncoder.default(self, o)


class HttpListener:
    """A listener that listens for HTTP commands on the given port."""

    def __init__(
        self,
        name: str,
        port: int,
        auth_token: str,
        event_manager: ev.EventManager,
        storage: str = "",
    ):
        self.app = flask.Flask(__name__)
        self.app.json_encoder = EvlJsonSerializer

        self.name = name
        self.port = port
        self.auth_token = auth_token
        self.event_manager = event_manager
        self.storage = storage

        self.current_tasks = {}

        self.app.add_url_rule("/events", "/events", self.get_events)
        self.app.add_url_rule(
            "/status_report", "/status_report", self.get_status_report
        )
        self.app.add_url_rule(
            "/tasks", "/tasks", self.do_tasks, methods=["POST", "DELETE"]
        )

    def __str__(self):
        """Returns s string representation of the HTTP listener."""

        return self.name

    def _authorize(self) -> None:
        """
        Compares given auth_token parameter with listener's auth_token value
        and aborts with a 403 Unauthorized response if they do not match.
        """

        auth_token = flask.request.args.get("auth_token")
        if auth_token != self.auth_token:
            flask.abort(403)

    def listen(self) -> None:
        """Starts the HTTP listener."""

        logger.debug("Starting HTTP listener...")
        server = wsgi.WSGIServer(("", self.port), self.app)
        server.serve_forever()

    def get_events(self) -> flask.Response:
        """
        Returns a JSON representation of past events.
        :returns: JSON representation of past events
        """

        self._authorize()
        storage = self.event_manager.storage.get(self.storage, None)
        if storage:
            return flask.jsonify(storage.all())
        else:
            return flask.jsonify({})

    def get_status_report(self) -> flask.Response:
        """
        Returns a JSON representation of the current system status.
        :returns: JSON representation of current system status
        """

        self._authorize()
        return flask.jsonify(self.event_manager.status_report())

    def do_tasks(self) -> flask.Response:
        """
        Performs the task specified in the request body.
        :returns: Result of performing given task
        """

        self._authorize()
        task = flask.request.get_json()

        if "type" not in task:
            flask.abort(400)

        if flask.request.method == "POST":
            return flask.jsonify(self._create_task(task))
        elif flask.request.method == "DELETE":
            return flask.jsonify(self._delete_task(task))

    def _create_task(self, task: dict) -> str:
        """
        Creates the task defined in the given dictionary.
        :param task: Dictionary containing task details
        :returns: Result of creating the given task
        """

        if task["type"] == "silent_arm":
            return self._create_silent_arm(task)
        else:
            flask.abort(400)

    def _delete_task(self, task) -> str:
        """
        Deletes the given task, if it exists.
        :param task: Details of task to delete
        :returns: Result of deleting the given task
        """

        if task["type"] == "silent_arm":
            silent_arm = self.current_tasks.get("silent-arm", None)
            if not silent_arm:
                flask.abort(400)
            silent_arm.stop()
            del self.current_tasks["silent-arm"]
            return "silent-arm task deleted"
        else:
            flask.abort(400)

    def _create_silent_arm(self, task: dict) -> str:
        """
        Creates a silent alarm task with the given task details.
        :param: Silent alarm task details
        :returns: Result of creating silent alarm task
        """

        if self.current_tasks.get("silent-arm", None):
            flask.abort(400)

        zones = task.get("zones", [])
        partitions = task.get("partitions", [])

        silentarm_task = silentarm.SilentArmTask(self.event_manager, partitions, zones)
        self.current_tasks["silent-arm"] = silentarm_task
        silentarm_task.start()

        return "silent-arm task created"
