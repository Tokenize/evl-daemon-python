import json
import logging
import os
import sys

from marshmallow import Schema, fields, post_load

import evl.command as cmd
import evl.listeners.asynchttp as http
import evl.notifiers.consolenotifier as console
import evl.notifiers.smsnotifier as sms
import evl.notifiers.emailnotifier as email
import evl.notifiers.mimirnotifier as mimir
import evl.storage.memory as memory
import evl.tasks.heartbeat as heartbeat


DEFAULT_HEARTBEAT_INTERVAL = 60
DEFAULT_LOGGING_LEVEL = "DEBUG"
DEFAULT_NOTIFIER_PRIORITY = "LOW"
DEFAULT_STORAGE_MAX_LENGTH = 100

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, **kwargs):

        self.heartbeats = load_heartbeats(kwargs.pop("heartbeats", []))
        self.logging = load_logging(kwargs.pop("logging", []))
        self.notifiers = load_notifiers(kwargs.pop("notifiers", []))
        self.storage = load_storage(kwargs.pop("storage", []))

        self.__dict__.update(kwargs)


class HeartbeatConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ListenerConfig:
    def __init__(self, **kwargs):
        self.kind = kwargs.pop("type")
        self.__dict__.update(kwargs)


class LoggingConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class NotifierConfig:
    def __init__(self, **kwargs):
        self.priority = kwargs.pop("priority").upper()
        self.__dict__.update(kwargs)


class StorageConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class HeartbeatSchema(Schema):
    auth_token = fields.String(required=True)
    device_id = fields.Integer(required=True)
    device_uuid = fields.String(required=True)
    interval = fields.Integer(required=False, missing=DEFAULT_HEARTBEAT_INTERVAL)
    name = fields.String(required=True)
    url = fields.Url(required=True)

    @post_load
    def make_hearbeat_config(self, data, **kwargs):
        return HeartbeatConfig(**data)


class ListenerSchema(Schema):
    name = fields.String(required=True)
    settings = fields.Dict(
        keys=fields.String(required=True), values=fields.String(required=True)
    )
    type = fields.String(required=True)

    @post_load
    def make_listener_config(self, data, **kwargs):
        return ListenerConfig(**data)


class LoggingSchema(Schema):
    level = fields.String(required=False, missing=DEFAULT_LOGGING_LEVEL)
    name = fields.String(required=True)
    type = fields.String(required=True)

    @post_load
    def make_logging_config(self, data, **kwargs):
        return LoggingConfig(**data)


class NotifierSchema(Schema):
    layout = fields.String(required=False, missing=None)
    name = fields.String(required=True)
    priority = fields.String(required=False, missing=DEFAULT_NOTIFIER_PRIORITY)
    settings = fields.Dict(
        keys=fields.String(required=True),
        values=fields.String(required=True),
        missing={},
    )
    type = fields.String(required=True)

    @post_load
    def make_notifier_config(self, data, **kwargs):
        return NotifierConfig(**data)


class StorageSchema(Schema):
    name = fields.String(required=True)
    settings = fields.Dict(
        keys=fields.String(required=True), values=fields.String(required=True)
    )
    type = fields.String(required=True)

    @post_load
    def make_storage_config(self, data, **kwargs):
        return StorageConfig(**data)


class ConfigSchema(Schema):
    heartbeats = fields.List(fields.Nested(HeartbeatSchema), required=False, missing=[])
    ip = fields.IPv4(required=True)
    listeners = fields.List(fields.Nested(ListenerSchema), required=False, missing=[])
    logging = fields.List(fields.Nested(LoggingSchema), required=False, missing=[])
    notifiers = fields.List(fields.Nested(NotifierSchema), required=False, missing=[])
    partitions = fields.Mapping(
        keys=fields.String(required=True),
        values=fields.String(required=True),
        required=True,
    )
    password = fields.String(missing="")
    port = fields.Integer(required=False, missing=4025)
    storage = fields.List(fields.Nested(StorageSchema), required=False, missing=[])
    zones = fields.Mapping(
        keys=fields.String(required=True),
        values=fields.String(required=True),
        required=True,
    )

    @post_load
    def make_config(self, data, **kwargs):
        return Config(**data)


HeartbeatConfigs = list[HeartbeatConfig]
ListenerConfigs = list[ListenerConfig]
LoggingConfigs = list[LoggingConfig]
NotifierConfigs = list[NotifierConfig]
StorageConfigs = list[StorageConfig]


def load_heartbeats(config: HeartbeatConfigs) -> list[heartbeat.HeartbeatTask]:
    heartbeats = []
    for hb in config:
        new_heartbeat = heartbeat.HeartbeatTask(
            hb.name, hb.device_id, hb.device_uuid, hb.interval, hb.url, hb.auth_token
        )
        heartbeats.append(new_heartbeat)

    return heartbeats


def load_listeners(config: ListenerConfigs, event_manager) -> list:
    listeners = []
    for listener in config:
        if listener.kind == "http":
            settings = listener.settings
            port = int(settings.get("port", 5204))
            auth_token = settings.get("auth_token", "")
            new_listener = http.AsyncHttpListener(
                listener.name,
                port,
                auth_token,
                event_manager,
                "memory",
            )

        else:
            new_listener = None

        if new_listener:
            listeners.append(new_listener)

    return listeners


def load_logging(config: LoggingConfigs) -> dict:
    """
    Loads logging configuration from config file and returns a dictionary
    following the logging configuration dictionary schema.
    :param config: Logging configuration list from config file
    :return dict: Logging configuration dictionary
    """

    log_config = {
        "version": 1,
        "handlers": {},
        "loggers": {},
        "root": {"level": logging.NOTSET},
    }

    handlers = []
    for new_logger in config:
        priority = new_logger.level
        name = new_logger.name
        kind = new_logger.type

        if kind == "console":
            log_config["handlers"][name] = {
                "class": "logging.StreamHandler",
                "level": priority,
                "stream": sys.stderr,
            }
            handlers.append(name)

    if handlers:
        log_config["loggers"]["evl"] = {"handlers": handlers}

    return log_config


def load_notifiers(config: NotifierConfigs) -> dict:
    """
    Load notifiers from given list of notifier configurations
    :param config: List of notifier configuration objects
    """
    notifiers = {}
    for notifier in config:
        name = notifier.name
        priority = cmd.Priority[notifier.priority]
        kind = notifier.type
        layout = notifier.layout
        settings = notifier.settings

        if kind == "console":
            new_notifier = console.ConsoleNotifier(priority=priority, name=name)
        elif kind == "sms":
            sender = settings.get("sender")
            recipient = settings.get("recipient")
            sid = settings.get("sid")
            auth_token = settings.get("authToken")
            new_notifier = sms.SmsNotifier(
                sid, auth_token, sender, recipient, priority, layout, name
            )
        elif kind == "email":
            sender = settings.get("sender")
            recipient = settings.get("recipient")
            api_key = settings.get("apiKey")
            subject = settings.get("subject")
            new_notifier = email.EmailNotifier(
                api_key, sender, recipient, priority, layout, subject, name
            )
        elif kind == "mimir":
            auth_token = settings.get("auth_token")
            device_uuid = settings.get("device_uuid")
            url = settings.get("url")
            new_notifier = mimir.MimirNotifier(
                url, device_uuid, auth_token, priority, layout, name
            )
        else:
            new_notifier = None

        if new_notifier:
            notifiers[name] = new_notifier

    return notifiers


def load_storage(config: StorageConfigs) -> dict:
    """
    Load storage engines from given list of storage configurations
    :param config: List of storage engine configuration dicts
    """
    storages = {}
    for storage in config:
        kind = storage.type
        name = storage.name
        settings = storage.settings

        # Set up storage engines defined in configuration file
        if kind == "memory":
            max_size = int(settings.get("maxSize", DEFAULT_STORAGE_MAX_LENGTH))
            new_storage = memory.MemoryStorage(size=max_size, name=name)
        else:
            new_storage = None

        if new_storage:
            storages[name] = new_storage
    return storages


def read(file: str) -> ConfigSchema:
    """
    Reads configuration from given file path and returns dictionary of
    configuration objects.
    :param file: Configuration file path
    :return: ConfigSchema object containing parsed configuration
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

    config_schema = ConfigSchema()
    config = config_schema.load(data)

    return config
