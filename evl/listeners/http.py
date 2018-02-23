import flask
import gevent.wsgi as wsgi
import logging


logger = logging.getLogger(__name__)


class HttpListener:
    def __init__(self, event_manager, port: int):
        self.app = flask.Flask(__name__)

        self.event_manager = event_manager
        self.port = port

        self.app.add_url_rule('/status_report', '/status_report', self.status_report)

    def listen(self):
        logger.debug("Starting HTTP listener...")
        server = wsgi.WSGIServer(('', self.port), self.app)
        server.serve_forever()

    def status_report(self):
        return flask.jsonify(self.event_manager.status_report())
