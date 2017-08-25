from datetime import datetime

from .command import Command, CommandType, LedState, LoginType,\
    Priority, PartitionArmedType
from .util import merge_dicts


COMMAND_NAMES = {
    CommandType.POLL: "Poll",
    CommandType.STATUS_REPORT: "Status Report",
    CommandType.NETWORK_LOGIN: "Network Login",
    CommandType.COMMAND_ACKNOWLEDGE: "Command Acknowledge",
    CommandType.LOGIN: "Login",
    CommandType.KEYPAD_LED_FLASH_STATE: "Keypad LED Flash State",
    CommandType.KEYPAD_LED_STATE: "Keypad LED State",
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
    CommandType.TROUBLE_LED_OFF: "Trouble LED Off"
}

COMMAND_PRIORITIES = {
    CommandType.POLL: Priority.LOW,
    CommandType.STATUS_REPORT: Priority.LOW,
    CommandType.NETWORK_LOGIN: Priority.LOW,
    CommandType.COMMAND_ACKNOWLEDGE: Priority.LOW,
    CommandType.LOGIN: Priority.LOW,
    CommandType.KEYPAD_LED_FLASH_STATE: Priority.LOW,
    CommandType.KEYPAD_LED_STATE: Priority.LOW,
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
    CommandType.TROUBLE_LED_OFF: Priority.LOW
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
    def __init__(self, command: Command, data: str= "", priority: Priority=Priority.LOW, timestamp=None):
        self.command = command
        self.data = data
        self.description = ""

        if priority is None:
            priority = Priority.LOW
        self.priority = priority

        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp

    def __str__(self) -> str:
        return self.description


class EventManager:
    """
    Represents an event manager that waits for incoming events from an event queue
    and dispatches events to its list of event notifiers.
    """
    def __init__(self, event_queue, notifiers: list=None, priorities: dict=None, command_names: dict=None,
                 login_names: dict=None, zones: dict=None, partitions: dict=None):

        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers
        self._event_queue = event_queue

        self._priorities = merge_dicts(COMMAND_PRIORITIES, overrides=priorities)
        self._command_names = merge_dicts(COMMAND_NAMES, overrides=command_names)
        self._login_names = merge_dicts(LOGIN_TYPE_NAMES, overrides=login_names)

        self.zones = zones
        self.partitions = partitions

    @property
    def priorities(self) -> dict:
        return self._priorities

    @priorities.setter
    def priorities(self, value: dict):
        self._priorities = merge_dicts(COMMAND_PRIORITIES, value)

    @property
    def command_names(self) -> dict:
        return self._command_names

    @command_names.setter
    def command_names(self, value: dict):
        self._command_names = merge_dicts(COMMAND_NAMES, value)

    @property
    def login_names(self) -> dict:
        return self._login_names

    @login_names.setter
    def login_names(self, value):
        self._login_names = merge_dicts(LOGIN_TYPE_NAMES, value)

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
        if event.command.command_type == CommandType.LOGIN:
            login_type = LoginType(event.data)
            description = "{command}: {login}".format(command=cmd_desc, login=self._login_names[login_type])
        else:
            description = "{command}".format(command=cmd_desc)
        return description

    def _describe_command(self, command: Command) -> str:
        """
        Describes the given command.
        :param command: Command to describe
        :return: Description of command
        """
        name = self._command_names.get(command.command_type)
        if name is None:
            name = "<Unknown: [{command}]>".format(command=command.number)
        return name

    def wait(self):
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = self._event_queue.get()
            priority = self._priorities.get(command.command_type)
            event = Event(command, data, timestamp=datetime.now(), priority=priority)
            event.description = self._describe(event)
            for notifier in self._notifiers:
                notifier.notify(event)
