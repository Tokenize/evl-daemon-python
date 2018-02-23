import flask
import gevent.wsgi as wsgi
import logging


logger = logging.getLogger(__name__)


class HttpListener:
    def __init__(self, name: str, port: int, auth_token: str, event_manager):
        self.app = flask.Flask(__name__)

        self.name = name
        self.port = port
        self.auth_token = auth_token
        self.event_manager = event_manager

        self.app.add_url_rule('/status_report', '/status_report', self.status_report)

    def __str__(self):
        return self.name

    def _authorize(self):
        auth_token = flask.request.args.get('auth_token')
        if auth_token != self.auth_token:
            return flask.abort(403)

    def listen(self):
        logger.debug("Starting HTTP listener...")
        server = wsgi.WSGIServer(('', self.port), self.app)
        server.serve_forever()

    def status_report(self):
        self._authorize()
        return flask.jsonify(self.event_manager.status_report())
