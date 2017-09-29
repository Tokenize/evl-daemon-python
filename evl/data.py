from enum import Enum

from .command import Command, CommandType


LOGIN_COMMANDS = {
    CommandType.LOGIN
}

PARTITION_COMMANDS = {
    CommandType.PARTITION_READY,
    CommandType.PARTITION_NOT_READY,
    CommandType.PARTITION_ARMED,
    CommandType.PARTITION_IN_ALARM,
    CommandType.PARTITION_DISARMED,
    CommandType.EXIT_DELAY_IN_PROGRESS,
    CommandType.ENTRY_DELAY_IN_PROGRESS,
}

PARTITION_AND_ZONE_COMMANDS = {
    CommandType.ZONE_ALARM,
    CommandType.ZONE_ALARM_RESTORE,
    CommandType.ZONE_TAMPER,
    CommandType.ZONE_TAMPER_RESTORE,
}

ZONE_COMMANDS = {
    CommandType.ZONE_FAULT,
    CommandType.ZONE_FAULT_RESTORE,
    CommandType.ZONE_OPEN,
    CommandType.ZONE_RESTORED
}


class LedState(Enum):
    READY = "7"
    ARMED = "6"
    MEMORY = "5"
    BYPASS = "4"
    TROUBLE = "3"
    PROGRAM = "2"
    FIRE = "1"
    BACKLIGHT = "0"


class LoginType(Enum):
    INCORRECT_PASSWORD = "0"
    LOGIN_SUCCESSFUL = "1"
    TIME_OUT = "2"
    PASSWORD_REQUEST = "3"


class PartitionArmedType(Enum):
    AWAY = "0"
    STAY = "1"
    ZERO_ENTRY_AWAY = "2"
    ZERO_ENTRY_STAY = "3"


def parse(command: Command, data: str) -> dict:
    parsed = {}
    command_type = command.command_type

    parsed['data'] = data
    if command_type in ZONE_COMMANDS:
        # Zone commands always have zone as first 3 chars
        parsed['zone'] = data[0:3]

    if command_type in PARTITION_COMMANDS:
        # Partition commands always have partition as first char
        parsed['partition'] = data[:1]

    if command_type in PARTITION_AND_ZONE_COMMANDS:
        parsed['partition'] = data[:1]
        parsed['zone'] = data[1:4]

    return parsed
