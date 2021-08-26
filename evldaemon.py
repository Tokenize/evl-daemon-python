import argparse
import asyncio
import logging
import logging.config
import socket

import evl.config as conf
import evl.connection as conn
import evl.event as ev

logger = logging.getLogger("evl")


class EvlDaemon:
    def __init__(self, host: str, password: str, port: int, config: conf.ConfigSchema):

        self.host = host
        self.password = password
        self.port = port
        self.connection = None

        if config is None:
            raise ValueError("Invalid config value!")
        self.config = config

        self.event_queue = asyncio.Queue()
        self.status = ev.Status()

        # Assign zone and partition names as read from configuration file.
        ev.EventManager.zones = self.config.zones
        ev.EventManager.partitions = self.config.partitions

        # TODO: Read command name, priority, login name, etc. overrides from config.

        self.event_manager = ev.EventManager(self.event_queue, status=self.status)

        self.notifiers = conf.load_notifiers(self.config.notifiers)
        self.event_manager.add_notifiers(self.notifiers)

        self.storage = conf.load_storage(self.config.storage)
        self.event_manager.add_storages(self.storage)
        self.heartbeats = conf.load_heartbeats(self.config.heartbeats)

        self.listeners = conf.load_listeners(self.config.listeners, self.event_manager)
        self.status.listeners = self.listeners

    async def start(self):
        logger.debug("Starting daemon...")
        resolved = socket.gethostbyname(self.host)
        self.connection = conn.Connection(
            event_manager=self.event_manager, host=resolved, password=self.password
        )

        self.status.connection = {"hostname": resolved, "port": self.connection.port}

        await asyncio.gather(
            self.connection.start(),
            self.event_manager.wait(),
            *[listener.listen() for listener in self.listeners],
            *[heartbeat.start() for heartbeat in self.heartbeats]
        )

    def stop(self):
        logger.debug("Stopping daemon...")
        self.connection.stop()
        logger.debug("Daemon stopped.")


def main():
    print("Welcome to EvlDaemon.")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", required=False, default="~/.config/evl_daemon/config.json"
    )
    options = parser.parse_args()
    config = conf.read(options.config)

    if config is None:
        print("Unable to read configuration file. Exiting.")
        exit(1)

    # logging.config.dictConfig(config.)

    host = config.ip
    if host is None:
        print("IP address not found in configuration file!")
        exit(1)

    password = config.password
    if password is None:
        print("Password not found in configuration file!")
        exit(1)

    port = config.port

    ed = EvlDaemon(host, password, port, config)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(ed.start())
    except KeyboardInterrupt:
        logger.debug("Ctrl+C pressed, stopping...")
        ed.stop()


if __name__ == "__main__":
    main()
