import argparse
import socket
import signal
import gevent.pool
import gevent.queue
import gevent.signal

import evl.connection as conn
import evl.event as ev
import evl.config as conf


class EvlDaemon:
    def __init__(self, host: str, password: str, port: int, config: dict=None):

        self.host = host
        self.password = password
        self.port = port

        if config is None:
            config = {}
        self.config = config

        self.notifiers = conf.load_notifiers(self.config.get('notifiers', []))
        self.storage = conf.load_storage(self.config.get('storage', []))

        self.queue_group = gevent.pool.Group()
        self.event_queue = gevent.queue.Queue()

        self.event_manager = ev.EventManager(self.event_queue, self.queue_group)
        self.event_manager.add_notifiers(self.notifiers)
        self.event_manager.add_storages(self.storage)

    def start(self):
        resolved = socket.gethostbyname(host)
        connection = conn.Connection(event_manager=self.event_manager,
                                     queue_group=self.queue_group,
                                     host=resolved,
                                     password=password)

        # Assign zone and partition names as read from configuration file.
        ev.EventManager.zones = config.get('zones', {})
        ev.EventManager.partitions = config.get('partitions', {})

        # TODO: Read command name, priority, login name, etc. overrides from config.

        # Are multiple signal handlers possible?
        gevent.signal(signal.SIGINT, connection.stop)
        gevent.signal(signal.SIGINT, self.queue_group.kill)

        connection.start()
        self.queue_group.join()


if __name__ == '__main__':
    print("Welcome to EvlDaemon")

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=False,
                        default="~/.evldaemon/config.json")
    options = parser.parse_args()
    config = conf.read(options.config)

    if config is None:
        print("Unable to read configuration file. Exiting.")
        exit(1)

    host = config.get('ip')
    if host is None:
        print("IP address not found in configuration file!")
        exit(1)

    password = config.get('password')
    if password is None:
        print("Password not found in configuration file!")
        exit(1)

    port = config.get('port', 4025)

    ed = EvlDaemon(host, password, port, config)
    ed.start()
