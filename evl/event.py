from datetime import datetime
from enum import Enum

from .command import Command, CommandType
from .data import (parse, LedState, LoginType, PartitionArmedType,
                   LOGIN_COMMANDS, PARTITION_COMMANDS, PARTITION_AND_ZONE_COMMANDS, ZONE_COMMANDS)


class Priority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

    def __str__(self):
        return self.name.title()

COMMAND_NAMES = {
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

COMMAND_PRIORITIES = {
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


class Event:
    """
    Represents an event from the EVL module, including the command, data,
    priority, timestamp and string description of the event.
    """

    def __init__(self, command: Command, data: dict, timestamp=None):
        self.command = command
        self.description = ""

        self.data = data.get('data', None)
        self.zone = data.get('zone', None)
        self.partition = data.get('partition', None)

        self.priority = EventManager.priorities.get(command.command_type, Priority.LOW)

        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp

    def zone_name(self) -> str:
        if self.zone is None:
            return ""
        return EventManager.zones.get(self.zone, "Zone {zone}".format(zone=self.zone))

    def partition_name(self) -> str:
        if self.partition is None:
            return ""
        return EventManager.partitions.get(self.partition,
                                           "Partition {partition}".format(partition=self.partition))

    def __str__(self) -> str:
        return self.description


class EventManager:
    """
    Represents an event manager that waits for incoming events from an event queue
    and dispatches events to its list of event notifiers.
    """

    command_names = COMMAND_NAMES
    login_names = LOGIN_TYPE_NAMES
    priorities = COMMAND_PRIORITIES

    partitions = {}
    zones = {}

    def __init__(self, event_queue, notifiers: list=None):

        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers
        self._event_queue = event_queue

    def add_notifier(self, notifier):
        """
        Adds a notifier object to the list of notifiers.
        :param notifier: Notifier to add to notifier list
        """
        self._notifiers.append(notifier)

    def _describe(self, event: Event) -> str:
        """
        Describes the given event based on the event's command and data.
        :param event: Event to describe
        :return: Description of event
        """
        cmd_desc = self._describe_command(event.command)
        command_type = event.command.command_type
        if command_type in LOGIN_COMMANDS:
            login_type = LoginType(event.data)
            description = "{command}: {login}".format(command=cmd_desc,
                                                      login=EventManager.login_names[login_type])
        elif command_type in PARTITION_COMMANDS:
            description = "{command}: [{partition}]".format(command=cmd_desc, partition=event.partition_name())
        elif command_type in PARTITION_AND_ZONE_COMMANDS:
            description = "{command}: [{partition}] {zone}".format(command=cmd_desc,
                                                                   partition=event.partition_name(),
                                                                   zone=event.zone_name())
        elif command_type in ZONE_COMMANDS:
            description = "{command}: {zone}".format(command=cmd_desc, zone=event.zone_name())
        elif command_type in (CommandType.KEYPAD_LED_FLASH_STATE, CommandType.KEYPAD_LED_STATE):
            led_state = self._describe_led_state(event.data)
            description = "{command}: {state}".format(command=cmd_desc, state=led_state)
        else:
            description = "{command}".format(command=cmd_desc)
        return description

    def _describe_command(self, command: Command) -> str:
        """
        Describes the given command.
        :param command: Command to describe
        :return: Description of command
        """
        name = EventManager.command_names.get(command.command_type)
        if name is None:
            name = "<Unknown: [{command}]>".format(command=command.number)
        return name

    def _describe_led_state(self, state: str) -> str:
        """
        Describes the given hex value LED state.

        Converts the given hex value to a string of bits representing the LED
        states and returns the enabled LEDs in a comma-separated string. Details
        about LED state can be found in the EnvisaLink TPI documentation.
        :param state: Hex value of LED state
        :return: Comma-separated string of enabled LEDs
        """
        state_base = 16
        state_width = 8

        bin_state = bin(int(state, state_base))[2:].zfill(state_width)
        leds = [LedState(str(ind)).name.title() for ind, st in enumerate(bin_state) if st == "1"]
        return ", ".join(leds)

    def wait(self):
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = self._event_queue.get()
            parsed_data = parse(command, data)
            event = Event(command, parsed_data, datetime.now())
            event.description = self._describe(event)
            for notifier in self._notifiers:
                notifier.notify(event)
