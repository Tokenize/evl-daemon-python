from enum import Enum


class Command:
    def __init__(self, number: str):
        self.number = number

        try:
            self.command_type = CommandType(number)
        except ValueError:
            self.command_type = CommandType.UNKNOWN

    def __str__(self) -> str:
        return self.describe()

    def describe(self) -> str:
        """
        Describes the given command.
        :return: Description of command
        """
        name = NAMES.get(self.command_type)
        if name is None:
            name = "<Unknown: [{command}]>".format(command=self.number)
        return name


class CommandType(Enum):
    POLL = "000"
    STATUS_REPORT = "001"
    NETWORK_LOGIN = "005"
    COMMAND_ACKNOWLEDGE = "500"
    COMMAND_ERROR = "501"
    SYSTEM_ERROR = "502"
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
    ENVISALINK_ZONE_TIMER_DUMP = "615"
    BYPASSED_ZONES_BITFIELD_DUMP = "616"
    DURESS_ALARM = "620"
    F_KEY_ALARM = "621"
    F_KEY_RESTORE = "622"
    A_KEY_ALARM = "623"
    A_KEY_RESTORE = "624"
    P_KEY_ALARM = "625"
    P_KEY_RESTORE = "626"
    SMOKE_AUX_ALARM = "631"
    SMOKE_AUX_RESTORE = "632"
    PARTITION_READY = "650"
    PARTITION_NOT_READY = "651"
    PARTITION_ARMED = "652"
    PARTITION_READY_FORCE_ARMING_ENABLED = "653"
    PARTITION_IN_ALARM = "654"
    PARTITION_DISARMED = "655"
    EXIT_DELAY_IN_PROGRESS = "656"
    ENTRY_DELAY_IN_PROGRESS = "657"
    KEYPAD_LOCK_OUT = "658"
    PARTITION_FAILED_TO_ARM = "659"
    PGM_OUTPUT_IN_PROGRESS = "660"
    CHIME_ENABLED = "663"
    CHIME_DISABLED = "664"
    INVALID_ACCESS_CODE = "670"
    FUNCTION_NOT_AVAILABLE = "671"
    FAILURE_TO_ARM = "672"
    PARTITION_IS_BUSY = "673"
    SYSTEM_ARMING_IN_PROGRESS = "674"
    SYSTEM_IN_INSTALLERS_MODE = "680"
    USER_CLOSING = "700"
    SPECIAL_CLOSING = "701"
    PARTIAL_CLOSING = "702"
    USER_OPENING = "750"
    SPECIAL_OPENING = "751"
    PANEL_BATTERY_TROUBLE = "800"
    PANEL_BATTERY_TROUBLE_RESTORE = "801"
    PANEL_AC_TROUBLE = "802"
    PANEL_AC_RESTORE = "803"
    SYSTEM_BELL_TROUBLE = "806"
    SYSTEM_BELL_TROUBLE_RESTORE = "807"
    FTC_TROUBLE = "814"
    FTC_TROUBLE_RESTORE = "815"
    BUFFER_NEAR_FULL = "816"
    GENERAL_SYSTEM_TAMPER = "829"
    GENERAL_SYSTEM_TAMPER_RESTORE = "830"
    TROUBLE_LED_ON = "840"
    TROUBLE_LED_OFF = "841"
    FIRE_TROUBLE_ALARM = "842"
    FIRE_TROUBLE_ALARM_RESTORE = "843"
    VERBOSE_TROUBLE_STATUS = "849"
    CODE_REQUIRED = "900"
    COMMAND_OUTPUT_PRESSED = "912"
    MASTER_CODE_REQUIRED = "921"
    INSTALLERS_CODE_REQUIRED = "922"
    SOFTWARE_ZONE_ALARM = "S01"
    UNKNOWN = "UNK"


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
    CommandType.COMMAND_ERROR: "Command Error",
    CommandType.SYSTEM_ERROR: "System Error",
    CommandType.LOGIN: "Login",
    CommandType.KEYPAD_LED_STATE: "Keypad LED State",
    CommandType.KEYPAD_LED_FLASH_STATE: "Keypad LED Flash State",
    CommandType.ZONE_ALARM: "Zone Alarm",
    CommandType.ZONE_ALARM_RESTORE: "Zone Alarm Restore",
    CommandType.ZONE_TAMPER: "Zone Tamper",
    CommandType.ZONE_TAMPER_RESTORE: "Zone Tamper Restore",
    CommandType.ZONE_FAULT: "Zone Fault",
    CommandType.ZONE_FAULT_RESTORE: "Zone Fault Restore",
    CommandType.ZONE_OPEN: "Zone Open",
    CommandType.ZONE_RESTORED: "Zone Restored",
    CommandType.ENVISALINK_ZONE_TIMER_DUMP: "EnvisaLink Zone Timer Dump",
    CommandType.BYPASSED_ZONES_BITFIELD_DUMP: "Bypassed Zones Bitfield Dump",
    CommandType.DURESS_ALARM: "Duress Alarm",
    CommandType.F_KEY_ALARM: "[F] Key Alarm",
    CommandType.F_KEY_RESTORE: "[F] Key Restore",
    CommandType.A_KEY_ALARM: "[A] Key Alarm",
    CommandType.A_KEY_RESTORE: "[A] Key Restore",
    CommandType.P_KEY_ALARM: "[P] Key Alarm",
    CommandType.P_KEY_RESTORE: "[P] Key Restore",
    CommandType.SMOKE_AUX_ALARM: "2-Wire Smoke/Aux Alarm",
    CommandType.SMOKE_AUX_RESTORE: "2-Wire Smoke/Aux Restore",
    CommandType.PARTITION_READY: "Partition Ready",
    CommandType.PARTITION_NOT_READY: "Partition Not Ready",
    CommandType.PARTITION_ARMED: "Partition Armed",
    CommandType.PARTITION_READY_FORCE_ARMING_ENABLED: "Partition Ready - Force Arming Enabled",
    CommandType.PARTITION_IN_ALARM: "Partition In Alarm",
    CommandType.PARTITION_DISARMED: "Partition Disarmed",
    CommandType.EXIT_DELAY_IN_PROGRESS: "Exit Delay in Progress",
    CommandType.ENTRY_DELAY_IN_PROGRESS: "Entry Delay in Progress",
    CommandType.KEYPAD_LOCK_OUT: "Keypad Lock-out",
    CommandType.PARTITION_FAILED_TO_ARM: "Partition Failed to Arm",
    CommandType.PGM_OUTPUT_IN_PROGRESS: "PGM Output is in Progress",
    CommandType.CHIME_ENABLED: "Chime Enabled",
    CommandType.CHIME_DISABLED: "Chime Disabled",
    CommandType.INVALID_ACCESS_CODE: "Invalid Access Code",
    CommandType.FUNCTION_NOT_AVAILABLE: "Function Not Available",
    CommandType.FAILURE_TO_ARM: "Failure to Arm",
    CommandType.PARTITION_IS_BUSY: "Partition is Busy",
    CommandType.SYSTEM_ARMING_IN_PROGRESS: "System Arming in Progress",
    CommandType.SYSTEM_IN_INSTALLERS_MODE: "System in Installers Mode",
    CommandType.USER_CLOSING: "User Closing",
    CommandType.SPECIAL_CLOSING: "Special Closing",
    CommandType.PARTIAL_CLOSING: "Partial Closing",
    CommandType.USER_OPENING: "User Opening",
    CommandType.SPECIAL_OPENING: "Special Opening",
    CommandType.PANEL_BATTERY_TROUBLE: "Panel Battery Trouble",
    CommandType.PANEL_BATTERY_TROUBLE_RESTORE: "Panel Battery Trouble Restore",
    CommandType.PANEL_AC_TROUBLE: "Panel AC Trouble",
    CommandType.PANEL_AC_RESTORE: "Panel AC Restore",
    CommandType.SYSTEM_BELL_TROUBLE: "System Bell Trouble",
    CommandType.SYSTEM_BELL_TROUBLE_RESTORE: "System Bell Trouble Restore",
    CommandType.FTC_TROUBLE: "FTC Trouble",
    CommandType.FTC_TROUBLE_RESTORE: "FTC Trouble Restore",
    CommandType.BUFFER_NEAR_FULL: "Buffer Near Full",
    CommandType.GENERAL_SYSTEM_TAMPER: "General System Tamper",
    CommandType.GENERAL_SYSTEM_TAMPER_RESTORE: "General System Tamper Restore",
    CommandType.TROUBLE_LED_ON: "Trouble LED On",
    CommandType.TROUBLE_LED_OFF: "Trouble LED Off",
    CommandType.FIRE_TROUBLE_ALARM: "Fire Trouble Alarm",
    CommandType.FIRE_TROUBLE_ALARM_RESTORE: "Fire Trouble Alarm Restore",
    CommandType.VERBOSE_TROUBLE_STATUS: "Verbose Trouble Status",
    CommandType.CODE_REQUIRED: "Code Required",
    CommandType.COMMAND_OUTPUT_PRESSED: "Command Output Pressed",
    CommandType.MASTER_CODE_REQUIRED: "Master Code Required",
    CommandType.INSTALLERS_CODE_REQUIRED: "Installers Code Required",
    CommandType.SOFTWARE_ZONE_ALARM: "Software Zone Alarm",
    CommandType.UNKNOWN: "Unknown"
}

# Priorities are Priority.LOW by default. Only commands that are higher priority
# are included in this dictionary.
PRIORITIES = {
    CommandType.COMMAND_ERROR: Priority.CRITICAL,
    CommandType.SYSTEM_ERROR: Priority.CRITICAL,
    CommandType.LOGIN: Priority.MEDIUM,
    CommandType.ZONE_ALARM: Priority.HIGH,
    CommandType.ZONE_ALARM_RESTORE: Priority.MEDIUM,
    CommandType.ZONE_TAMPER: Priority.CRITICAL,
    CommandType.ZONE_TAMPER_RESTORE: Priority.MEDIUM,
    CommandType.ZONE_FAULT: Priority.CRITICAL,
    CommandType.ZONE_FAULT_RESTORE: Priority.MEDIUM,
    CommandType.ZONE_RESTORED: Priority.MEDIUM,
    CommandType.PARTITION_ARMED: Priority.MEDIUM,
    CommandType.PARTITION_IN_ALARM: Priority.HIGH,
    CommandType.PARTITION_DISARMED: Priority.MEDIUM,
    CommandType.EXIT_DELAY_IN_PROGRESS: Priority.MEDIUM,
    CommandType.ENTRY_DELAY_IN_PROGRESS: Priority.MEDIUM,
    CommandType.KEYPAD_LOCK_OUT: Priority.HIGH,
    CommandType.PARTITION_FAILED_TO_ARM: Priority.HIGH,
    CommandType.INVALID_ACCESS_CODE: Priority.HIGH,
    CommandType.FUNCTION_NOT_AVAILABLE: Priority.HIGH,
    CommandType.FAILURE_TO_ARM: Priority.HIGH,
    CommandType.PARTITION_IS_BUSY: Priority.MEDIUM,
    CommandType.SYSTEM_ARMING_IN_PROGRESS: Priority.MEDIUM,
    CommandType.SYSTEM_IN_INSTALLERS_MODE: Priority.HIGH,
    CommandType.USER_CLOSING: Priority.MEDIUM,
    CommandType.SPECIAL_CLOSING: Priority.MEDIUM,
    CommandType.PARTIAL_CLOSING: Priority.MEDIUM,
    CommandType.USER_OPENING: Priority.MEDIUM,
    CommandType.SPECIAL_OPENING: Priority.MEDIUM,
    CommandType.PANEL_BATTERY_TROUBLE: Priority.CRITICAL,
    CommandType.PANEL_BATTERY_TROUBLE_RESTORE: Priority.MEDIUM,
    CommandType.PANEL_AC_TROUBLE: Priority.CRITICAL,
    CommandType.PANEL_AC_RESTORE: Priority.MEDIUM,
    CommandType.SYSTEM_BELL_TROUBLE: Priority.CRITICAL,
    CommandType.SYSTEM_BELL_TROUBLE_RESTORE: Priority.MEDIUM,
    CommandType.FTC_TROUBLE: Priority.CRITICAL,
    CommandType.BUFFER_NEAR_FULL: Priority.CRITICAL,
    CommandType.GENERAL_SYSTEM_TAMPER: Priority.CRITICAL,
    CommandType.GENERAL_SYSTEM_TAMPER_RESTORE: Priority.MEDIUM,
    CommandType.TROUBLE_LED_ON: Priority.CRITICAL,
    CommandType.TROUBLE_LED_OFF: Priority.MEDIUM,
    CommandType.FIRE_TROUBLE_ALARM: Priority.HIGH,
    CommandType.FIRE_TROUBLE_ALARM_RESTORE: Priority.MEDIUM,
    CommandType.VERBOSE_TROUBLE_STATUS: Priority.CRITICAL,
    CommandType.CODE_REQUIRED: Priority.HIGH,
    CommandType.COMMAND_OUTPUT_PRESSED: Priority.HIGH,
    CommandType.MASTER_CODE_REQUIRED: Priority.HIGH,
    CommandType.INSTALLERS_CODE_REQUIRED: Priority.HIGH,
    CommandType.SOFTWARE_ZONE_ALARM: Priority.HIGH,
}

LOGIN_COMMANDS = {CommandType.LOGIN}

PARTITION_COMMANDS = {
    CommandType.PARTITION_READY,
    CommandType.PARTITION_NOT_READY,
    CommandType.PARTITION_ARMED,
    CommandType.PARTITION_READY_FORCE_ARMING_ENABLED,
    CommandType.PARTITION_IN_ALARM,
    CommandType.PARTITION_DISARMED,
    CommandType.EXIT_DELAY_IN_PROGRESS,
    CommandType.ENTRY_DELAY_IN_PROGRESS,
    CommandType.KEYPAD_LOCK_OUT,
    CommandType.PARTITION_FAILED_TO_ARM,
    CommandType.PGM_OUTPUT_IN_PROGRESS,
    CommandType.CHIME_ENABLED,
    CommandType.CHIME_DISABLED,
    CommandType.INVALID_ACCESS_CODE,
    CommandType.FUNCTION_NOT_AVAILABLE,
    CommandType.FAILURE_TO_ARM,
    CommandType.PARTITION_IS_BUSY,
    CommandType.SYSTEM_ARMING_IN_PROGRESS,
    CommandType.USER_CLOSING,
    CommandType.SPECIAL_CLOSING,
    CommandType.PARTIAL_CLOSING,
    CommandType.USER_OPENING,
    CommandType.SPECIAL_OPENING,
    CommandType.TROUBLE_LED_ON,
    CommandType.TROUBLE_LED_OFF,
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
    CommandType.ZONE_RESTORED,
    CommandType.SOFTWARE_ZONE_ALARM,
}
