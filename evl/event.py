from datetime import datetime
from enum import Enum

from .command import Command, LoginType, Priority


COMMAND_NAMES = {
    Command.POLL: "Poll",
    Command.STATUS_REPORT: "Status Report",
    Command.NETWORK_LOGIN: "Network Login",
    Command.COMMAND_ACKNOWLEDGE: "Command Acknowledge",
    Command.LOGIN: "Login",
    Command.KEYPAD_LED_FLASH_STATE: "Keypad LED Flash State",
    Command.KEYPAD_LED_STATE: "Keypad LED State",
    Command.ZONE_OPEN: "Zone Open",
    Command.ZONE_RESTORED: "Zone Restored",
    Command.PARTITION_READY: "Partition Ready",
    Command.PARTITION_NOT_READY: "Partition Not Ready",
    Command.PARTITION_ARMED: "Partition Armed",
    Command.PARTITION_IN_ALARM: "Partition In Alarm",
    Command.PARTITION_DISARMED: "Partition Disarmed",
    Command.EXIT_DELAY_IN_PROGRESS: "Exit Delay in Progress",
    Command.ENTRY_DELAY_IN_PROGRESS: "Entry Delay in Progress",
    Command.PARTITION_IS_BUSY: "Partition is Busy",
    Command.SPECIAL_CLOSING: "Special Closing",
    Command.USER_OPENING: "User Opening",
    Command.TROUBLE_LED_OFF: "Trouble LED Off",
}

LOGIN_TYPE_NAMES = {
    LoginType.INCORRECT_PASSWORD: "Incorrect Password",
    LoginType.LOGIN_SUCCESSFUL: "Login Successful",
    LoginType.PASSWORD_REQUEST: "Password Request",
    LoginType.TIME_OUT: "Login Timeout"
}


class Event:
    def __init__(self, command, data="", priority=Priority.Low, timestamp=None):
        self.command = command
        self.data = data
        self.priority = priority
        self.description = ""

        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp

    def __str__(self):
        return self.description


class EventManager:

    def __init__(self, event_queue, notifiers=None, command_names=None,
                 login_names=None):
        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers
        self._event_queue = event_queue
        self._command_names = EventManager.merge_names(COMMAND_NAMES, overrides=command_names)
        self._login_names = EventManager.merge_names(LOGIN_TYPE_NAMES, overrides=login_names)

    def add_notifier(self, notifier):
        self._notifiers.append(notifier)

    def _describe(self, event: Event):
        cmd_desc = self._describe_command(event.command)
        if event.command == Command.LOGIN:
            login_type = LoginType(event.data)
            description = "{command}: {login}".format(command=cmd_desc, login=self._login_names[login_type])
        else:
            description = "{command}".format(command=cmd_desc)
        return description

    def _describe_command(self, command: Command):
        name = self._command_names.get(command)
        if name is None:
            name = "<Unknown: [{command}]>".format(command=command.value)
        return name

    def wait(self):
        while True:
            (command, data) = self._event_queue.get()
            event = Event(command, data, timestamp=datetime.now())
            event.description = self._describe(event)
            for notifier in self._notifiers:
                notifier.notify(event)

    @staticmethod
    def merge_names(default, overrides=None):
        if overrides:
            return {**default, **overrides}
        return default
