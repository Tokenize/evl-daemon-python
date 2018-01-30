from enum import Enum


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


class CommandType(Enum):
    POLL = "000"
    STATUS_REPORT = "001"
    NETWORK_LOGIN = "005"
    COMMAND_ACKNOWLEDGE = "500"
    LOGIN = "505"
    KEYPAD_LED_STATE = "510"
    KEYPAD_LED_FLASH_STATE = "511"
    ZONE_ALARM = "601"
    ZONE_ALARM_RESTORE = "602"
    ZONE_TAMPER = "603"
    ZONE_TAMPER_RESTORE = "604"
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


class Priority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

    def __str__(self):
        return self.name.title()


NAMES = {
    CommandType.POLL: "Poll",
    CommandType.STATUS_REPORT: "Status Report",
    CommandType.NETWORK_LOGIN: "Network Login",
    CommandType.COMMAND_ACKNOWLEDGE: "Command Acknowledge",
    CommandType.LOGIN: "Login",
    CommandType.KEYPAD_LED_FLASH_STATE: "Keypad LED Flash State",
    CommandType.KEYPAD_LED_STATE: "Keypad LED State",
    CommandType.ZONE_ALARM: "Zone Alarm",
    CommandType.ZONE_ALARM_RESTORE: "Zone Alarm Restore",
    CommandType.ZONE_TAMPER: "Zone Tamper",
    CommandType.ZONE_TAMPER_RESTORE: "Zone Tamper Restore",
    CommandType.ZONE_FAULT: "Zone Fault",
    CommandType.ZONE_FAULT_RESTORE: "Zone Fault Restore",
    CommandType.ZONE_OPEN: "Zone Open",
    CommandType.ZONE_RESTORED: "Zone Restored",
    CommandType.PARTITION_READY: "Partition Ready",
    CommandType.PARTITION_NOT_READY: "Partition Not Ready",
    CommandType.PARTITION_ARMED: "Partition Armed",
    CommandType.PARTITION_IN_ALARM: "Partition In Alarm",
    CommandType.PARTITION_DISARMED: "Partition Disarmed",
    CommandType.EXIT_DELAY_IN_PROGRESS: "Exit Delay in Progress",
    CommandType.ENTRY_DELAY_IN_PROGRESS: "Entry Delay in Progress",
    CommandType.PARTITION_IS_BUSY: "Partition is Busy",
    CommandType.SPECIAL_CLOSING: "Special Closing",
    CommandType.USER_OPENING: "User Opening",
    CommandType.TROUBLE_LED_OFF: "Trouble LED Off",
    CommandType.FIRE_TROUBLE_ALARM: "Fire Trouble Alarm",
    CommandType.FIRE_TROUBLE_ALARM_RESTORE: "Fire Trouble Alarm Restore"
}

PRIORITIES = {
    CommandType.POLL: Priority.LOW,
    CommandType.STATUS_REPORT: Priority.LOW,
    CommandType.NETWORK_LOGIN: Priority.LOW,
    CommandType.COMMAND_ACKNOWLEDGE: Priority.LOW,
    CommandType.LOGIN: Priority.LOW,
    CommandType.KEYPAD_LED_FLASH_STATE: Priority.LOW,
    CommandType.KEYPAD_LED_STATE: Priority.LOW,
    CommandType.ZONE_ALARM: Priority.CRITICAL,
    CommandType.ZONE_ALARM_RESTORE: Priority.LOW,
    CommandType.ZONE_TAMPER: Priority.HIGH,
    CommandType.ZONE_TAMPER_RESTORE: Priority.LOW,
    CommandType.ZONE_FAULT: Priority.MEDIUM,
    CommandType.ZONE_FAULT_RESTORE: Priority.LOW,
    CommandType.ZONE_OPEN: Priority.LOW,
    CommandType.ZONE_RESTORED: Priority.MEDIUM,
    CommandType.PARTITION_READY: Priority.LOW,
    CommandType.PARTITION_NOT_READY: Priority.LOW,
    CommandType.PARTITION_ARMED: Priority.MEDIUM,
    CommandType.PARTITION_IN_ALARM: Priority.CRITICAL,
    CommandType.PARTITION_DISARMED: Priority.MEDIUM,
    CommandType.EXIT_DELAY_IN_PROGRESS: Priority.MEDIUM,
    CommandType.ENTRY_DELAY_IN_PROGRESS: Priority.MEDIUM,
    CommandType.PARTITION_IS_BUSY: Priority.LOW,
    CommandType.SPECIAL_CLOSING: Priority.LOW,
    CommandType.USER_OPENING: Priority.LOW,
    CommandType.TROUBLE_LED_OFF: Priority.LOW,
    CommandType.FIRE_TROUBLE_ALARM: Priority.CRITICAL,
    CommandType.FIRE_TROUBLE_ALARM_RESTORE: Priority.LOW,
}

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

