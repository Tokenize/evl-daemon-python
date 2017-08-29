import argparse
import json
import os.path
import sys
import socket
import signal
import gevent.signal

from evl.event import Priority
from evl.connection import Connection
from evl.notifiers.consolenotifier import ConsoleNotifier


def read_config(file: str) -> dict:
    file = os.path.expanduser(file)

    data = None
    try:
        with open(file) as json_data:
            data = json.load(json_data)
    except FileNotFoundError:
        print("Configuration file '{file}' not found!".format(file=file))
    except json.JSONDecodeError:
        print("Invalid configuration file '{file}'!".format(file=file))

    return data

if __name__ == '__main__':
    print("Welcome to EvlDaemon")

    p = argparse.ArgumentParser()
    p.add_argument('-c', '--config', required=False, default="~/.evldaemon/config.json")
    options = p.parse_args()
    config = read_config(options.config)

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

    resolved = socket.gethostbyname(host)
    connection = Connection(host=resolved, password=password)

    for notifier in config.get('notifiers', []):
        # Set up notifiers defined in configuration file
        priority = Priority[notifier.get('priority', 'LOW').upper()]

        if notifier['type'] == 'console':
            new_notifier = ConsoleNotifier(priority=priority)
        else:
            new_notifier = None

        if new_notifier:
            connection.event_manager.add_notifier(new_notifier)

    connection.event_manager.zones = config.get('zones', {})
    connection.event_manager.partitions = config.get('partitions', {})

    gevent.signal(signal.SIGINT, connection.stop)

    connection.start()
