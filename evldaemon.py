import argparse
import json
import os.path
import socket
import signal
import gevent.pool
import gevent.queue
import gevent.signal

from evl.connection import Connection
from evl.event import EventManager, Priority
from evl.notifiers.consolenotifier import ConsoleNotifier
from evl.notifiers.smsnotifier import SmsNotifier
from evl.notifiers.emailnotifier import EmailNotifier
from evl.storage.memory import MemoryStorage


DEFAULT_STORAGE_MAX_LENGTH = 100


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

def load_notifiers(config: list):
    notifiers = []
    for notifier in config:
        priority = Priority[notifier.get('priority', 'LOW').upper()]
        name = notifier.get('name')
        kind = notifier['type']

        if kind == 'console':
            new_notifier = ConsoleNotifier(priority=priority, name=name)
        elif kind == 'sms':
            layout = notifier.get('layout')
            settings = notifier.get('settings')
            sender = settings.get('sender')
            recipient = settings.get('recipient')
            sid = settings.get('sid')
            auth_token = settings.get('authToken')
            new_notifier = SmsNotifier(sid, auth_token, sender, recipient, priority, layout, name)
        elif kind == 'email':
            layout = notifier.get('layout')
            settings = notifier.get('settings')
            sender = settings.get('sender')
            recipient = settings.get('recipient')
            api_key = settings.get('apiKey')
            subject = settings.get('subject')
            new_notifier = EmailNotifier(api_key, sender, recipient, priority, layout, subject, name)
        else:
            new_notifier = None

        if new_notifier:
            notifiers.append(new_notifier)
    return notifiers

def load_storage(config: list):
    storages = []
    for storage in config:
        kind = storage['type']
        # Set up storage engines defined in configuration file
        if kind == 'memory':
            max_size = storage.get('maxSize', DEFAULT_STORAGE_MAX_LENGTH)
            new_storage = MemoryStorage(size=max_size)
        else:
            new_storage = None

        if new_storage:
            storages.append(new_storage)
    return storages


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

    queue_group = gevent.pool.Group()
    event_queue = gevent.queue.Queue()
    event_manager = EventManager(event_queue, queue_group)

    resolved = socket.gethostbyname(host)
    connection = Connection(event_manager=event_manager, queue_group=queue_group, host=resolved, password=password)

    notifiers = load_notifiers(config.get('notifiers', []))
    event_manager.add_notifiers(notifiers)
    
    storages = load_storage(config.get('storage', []))
    event_manager.add_storages(storages)

    # Assign zone and partition names as read from configuration file.
    EventManager.zones = config.get('zones', {})
    EventManager.partitions = config.get('partitions', {})

    # TODO: Read command name, priority, login name, etc. overrides from config.

    # Are multiple signal handlers possible?
    gevent.signal(signal.SIGINT, connection.stop)
    gevent.signal(signal.SIGINT, queue_group.kill)

    connection.start()
    queue_group.join()
