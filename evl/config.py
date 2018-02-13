import json
import logging
import os
import sys

import evl.command as cmd
import evl.notifiers.consolenotifier as console
import evl.notifiers.smsnotifier as sms
import evl.notifiers.emailnotifier as email
import evl.storage.memory as memory


DEFAULT_STORAGE_MAX_LENGTH = 100

logger = logging.getLogger(__name__)


def load_logging(config: list) -> dict:
    """
    Loads logging configuration from config file and returns a dictionary
    following the logging configuration dictionary schema.
    :param config: Logging configuration list from config file
    :return dict: Logging configuration dictionary
    """

    log_config = {'version': 1, 'handlers': {}, 'loggers': {},
                  'root': {'level': logging.NOTSET}}

    handlers = []
    for new_logger in config:
        priority = new_logger.get('level', 'INFO')
        name = new_logger['name']
        kind = new_logger['type']

        if kind == 'console':
            log_config['handlers'][name] = {
                'class': 'logging.StreamHandler',
                'level': priority,
                'stream': sys.stderr
            }
            handlers.append(name)

    if handlers:
        log_config['loggers']['evl'] = {
            'handlers': handlers
        }

    return log_config


def load_notifiers(config: list) -> list:
    """
    Load notifiers from given list of notifier configurations
    :param config: List of notifier configuration dicts
    """
    notifiers = []
    for notifier in config:
        priority = cmd.Priority[notifier.get('priority', 'LOW').upper()]
        name = notifier.get('name')
        kind = notifier['type']

        if kind == 'console':
            new_notifier = console.ConsoleNotifier(priority=priority, name=name)
        elif kind == 'sms':
            layout = notifier.get('layout')
            settings = notifier.get('settings')
            sender = settings.get('sender')
            recipient = settings.get('recipient')
            sid = settings.get('sid')
            auth_token = settings.get('authToken')
            new_notifier = sms.SmsNotifier(sid, auth_token, sender, recipient,
                                           priority, layout, name)
        elif kind == 'email':
            layout = notifier.get('layout')
            settings = notifier.get('settings')
            sender = settings.get('sender')
            recipient = settings.get('recipient')
            api_key = settings.get('apiKey')
            subject = settings.get('subject')
            new_notifier = email.EmailNotifier(api_key, sender, recipient, priority,
                                               layout, subject, name)
        else:
            new_notifier = None

        if new_notifier:
            notifiers.append(new_notifier)
    return notifiers


def load_storage(config: list) -> list:
    """
    Load storage engines from given list of storage configurations
    :param config: List of storage engine configuration dicts
    """
    storages = []
    for storage in config:
        kind = storage['type']
        # Set up storage engines defined in configuration file
        if kind == 'memory':
            max_size = storage.get('maxSize', DEFAULT_STORAGE_MAX_LENGTH)
            new_storage = memory.MemoryStorage(size=max_size)
        else:
            new_storage = None

        if new_storage:
            storages.append(new_storage)
    return storages


def read(file: str) -> dict:
    """
    Reads configuration from given file path and returns dictionary of
    configuration objects.
    :param file: Configuration file path
    :return: Dictionary of configuration objects
    """
    file = os.path.expanduser(file)

    data = None
    try:
        with open(file) as json_data:
            data = json.load(json_data)
    except FileNotFoundError:
        logger.critical("Configuration file '{file}' not found!".format(file=file))
    except json.JSONDecodeError:
        logger.critical("Invalid configuration file '{file}'!".format(file=file))

    return data
