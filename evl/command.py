from enum import Enum


class CommandType(Enum):
    POLL = "000"
    STATUS_REPORT = "001"
    NETWORK_LOGIN = "005"
    COMMAND_ACKNOWLEDGE = "500"
    LOGIN = "505"
    KEYPAD_LED_STATE = "510"
    KEYPAD_LED_FLASH_STATE = "511"
    ZONE_FAULT = "605"
    ZONE_FAULT_RESTORE = "606"
    ZONE_OPEN = "609"
    ZONE_RESTORED = "610"
    PARTITION_READY = "650"
    PARTITION_NOT_READY = "651"
    PARTITION_ARMED = "652"
    PARTITION_IN_ALARM = "654"
    PARTITION_DISARMED = "655"
    EXIT_DELAY_IN_PROGRESS = "656"
    ENTRY_DELAY_IN_PROGRESS = "657"
    PARTITION_IS_BUSY = "673"
    SPECIAL_CLOSING = "701"
    USER_OPENING = "750"
    TROUBLE_LED_OFF = "841"
    FIRE_TROUBLE_ALARM = "842"
    FIRE_TROUBLE_ALARM_RESTORE = "843"


class LedState(Enum):
    READY = "0"
    ARMED = "1"
    MEMORY = "2"
    BYPASS = "3"
    TROUBLE = "4"
    PROGRAM = "5"
    FIRE = "6"
    BACKLIGHT = "7"


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


class Command:
    def __init__(self, number: str):
        self.number = number

        try:
            self.command_type = CommandType(number)
        except ValueError:
            self.command_type = None

    def __str__(self):
        if self.command_type is None:
            return "<Unknown: {type}>".format(type=self.number)
        return self.command_type.name
