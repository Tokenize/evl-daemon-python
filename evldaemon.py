import argparse
import socket
import signal
import gevent.pool
import gevent.queue
import gevent.signal
import logging
import logging.config

import evl.connection as conn
import evl.event as ev
import evl.config as conf


logger = logging.getLogger('evl')


class EvlDaemon:
    def __init__(self, host: str, password: str, port: int, config: dict=None):

        self.host = host
        self.password = password
        self.port = port
        self.connection = None

        if config is None:
            config = {}
        self.config = config

        self.greenlet_group = gevent.pool.Group()
        self.event_queue = gevent.queue.Queue()

        self.status = ev.Status()

        # Assign zone and partition names as read from configuration file.
        ev.EventManager.zones = self.config.get('zones', {})
        ev.EventManager.partitions = self.config.get('partitions', {})

        # TODO: Read command name, priority, login name, etc. overrides from config.

        self.event_manager = ev.EventManager(self.event_queue, self.greenlet_group, status=self.status)

        self.notifiers = conf.load_notifiers(self.config.get('notifiers', []))
        self.event_manager.add_notifiers(self.notifiers)

        self.storage = conf.load_storage(self.config.get('storage', []))
        self.event_manager.add_storages(self.storage)

        self.listeners = conf.load_listeners(self.config.get('listeners', []), self.event_manager)
        self.status.listeners = self.listeners
        for listener in self.listeners:
            self.greenlet_group.spawn(listener.listen)

    def start(self):
        logger.debug("Starting daemon...")
        resolved = socket.gethostbyname(self.host)
        self.connection = conn.Connection(event_manager=self.event_manager,
                                          queue_group=self.greenlet_group,
                                          host=resolved,
                                          password=self.password)

        self.status.connection = {'hostname': resolved, 'port': self.connection.port}

        gevent.signal(signal.SIGINT, self.stop)

        self.connection.start()
        self.greenlet_group.join()

    def stop(self):
        logger.debug("Stopping daemon...")
        self.connection.stop()
        self.greenlet_group.kill()
        logger.debug("Daemon stopped.")


def main():
    print("Welcome to EvlDaemon.")
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=False,
                        default="~/.evldaemon/config.json")
    options = parser.parse_args()
    config = conf.read(options.config)

    if config is None:
        print("Unable to read configuration file. Exiting.")
        exit(1)

    logging_config = conf.load_logging(config.get('logging', []))
    logging.config.dictConfig(logging_config)

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


if __name__ == '__main__':
    main()

