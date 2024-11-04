from enum import StrEnum, auto
from typing import Union, Dict
from pydantic import BaseModel
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict
from command import Priority


class LoggingLevel(StrEnum):
    CRITICAL = auto()
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()


DEFAULT_HEARTBEAT_INTERVAL = 60
DEFAULT_LOGGING_LEVEL = LoggingLevel.DEBUG
DEFAULT_NOTIFIER_PRIORITY = Priority.LOW
DEFAULT_STORAGE_MAX_LENGTH = 100

SettingsDict = Dict[str, Union[str, int, float, list, dict]]


class HeartbeatSettings(BaseModel):
    auth_token: str
    device_id: int
    device_uuid: str
    interval: int = DEFAULT_HEARTBEAT_INTERVAL
    name: str
    url: Url


class LoggerSettings(BaseModel):
    name: str
    level: LoggingLevel = DEFAULT_LOGGING_LEVEL
    type: str


class ListenerSettings(BaseModel):
    name: str
    settings: SettingsDict = {}
    type: str


class NotifierSettings(BaseModel):
    name: str
    priority: Priority
    settings: SettingsDict = {}
    type: str


class StorageSettings(BaseModel):
    name: str
    settings: SettingsDict = {}
    type: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        nested_model_default_partial_update=True, cli_parse_args=True
    )

    heartbeats: list[HeartbeatSettings]
    loggers: list[LoggerSettings]
    listeners: list[ListenerSettings]
    notifiers: list[NotifierSettings]
    storage: list[StorageSettings]
