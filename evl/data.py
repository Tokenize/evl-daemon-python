from enum import Enum

import evl.command as cmd


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


LED_STATE_NAMES = {
    LedState.ARMED: "Armed",
    LedState.BACKLIGHT: "Backlight",
    LedState.BYPASS: "Bypass",
    LedState.FIRE: "Fire",
    LedState.MEMORY: "Memory",
    LedState.PROGRAM: "Program",
    LedState.READY: "Ready",
    LedState.TROUBLE: "Trouble"
}

LOGIN_TYPE_NAMES = {
    LoginType.INCORRECT_PASSWORD: "Incorrect Password",
    LoginType.LOGIN_SUCCESSFUL: "Login Successful",
    LoginType.PASSWORD_REQUEST: "Password Request",
    LoginType.TIME_OUT: "Login Timeout"
}

PARTITION_ARMED_NAMES = {
    PartitionArmedType.AWAY: "Away",
    PartitionArmedType.STAY: "Stay",
    PartitionArmedType.ZERO_ENTRY_AWAY: "Zero Entry Away",
    PartitionArmedType.ZERO_ENTRY_STAY: "Zero Entry Stay"
}


def parse(command: cmd.Command, data: str) -> dict:
    parsed = {}
    command_type = command.command_type

    parsed['data'] = data
    if command_type in cmd.ZONE_COMMANDS:
        # Zone commands always have zone as first 3 chars
        parsed['zone'] = data[0:3]

    if command_type in cmd.PARTITION_COMMANDS:
        # Partition commands always have partition as first char
        parsed['partition'] = data[:1]

    if command_type in cmd.PARTITION_AND_ZONE_COMMANDS:
        parsed['partition'] = data[:1]
        parsed['zone'] = data[1:4]

    return parsed
