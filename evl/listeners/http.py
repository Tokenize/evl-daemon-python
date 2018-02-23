from flask import Flask
from gevent.wsgi import WSGIServer

import logging


logger = logging.getLogger(__name__)


class HttpListener:
    def __init__(self, event_manager, port: int):
        self.app = Flask(__name__)

        self.event_manager = event_manager
        self.port = port

        self.app.add_url_rule('/status_report', '/status_report', self.status_report)

    def listen(self):
        logger.debug("Starting HTTP listener...")
        server = WSGIServer(('', self.port), self.app)
        server.serve_forever()

    def status_report(self):
        return str(self.event_manager.status_report())
