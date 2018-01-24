from enum import Enum
import time

from evl import command as cmd
from .data import (parse, LedState, LoginType, PartitionArmedType,
                   LOGIN_COMMANDS, PARTITION_COMMANDS, PARTITION_AND_ZONE_COMMANDS, ZONE_COMMANDS)


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

    def __init__(self, command: cmd.Command, data: dict, timestamp=None):
        self.command = command
        self.description = ""

        self.data = data.get('data', None)
        self.zone = data.get('zone', None)
        self.partition = data.get('partition', None)

        self.priority = EventManager.priorities.get(command.command_type, cmd.Priority.LOW)

        if timestamp is None:
            timestamp = int(time.time())
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

    command_names = cmd.NAMES
    login_names = LOGIN_TYPE_NAMES
    priorities = cmd.PRIORITIES

    partitions = {}
    zones = {}

    def __init__(self, event_queue, queue_group=None, notifiers: list=None, storage: list=None):

        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers

        if storage is None:
            storage = []
        self._storage = storage

        self._event_queue = event_queue

        if queue_group is not None:
            self._queue_group = queue_group
            self._queue_group.spawn(self.wait)

    def add_notifiers(self, notifiers: list):
        """
        Adds a list of notifiers to the existing list.
        :param notifiers: List of notifiers to add to notifier list
        """
        self._notifiers.extend(notifiers)

    def add_storages(self, storages: list):
        """
        Adds an event storage engine
        :param storage: Storage engine to add to storage list
        """
        self._storage.extend(storages)

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
        elif command_type in (cmd.CommandType.KEYPAD_LED_FLASH_STATE, cmd.CommandType.KEYPAD_LED_STATE):
            led_state = self._describe_led_state(event.data)
            description = "{command}: {state}".format(command=cmd_desc, state=led_state)
        else:
            description = "{command}".format(command=cmd_desc)
        return description

    def _describe_command(self, command: cmd.Command) -> str:
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

    def enqueue(self, command: cmd.Command, data: str = ""):
        self._event_queue.put((command, data))

    def wait(self):
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = self._event_queue.get()
            parsed_data = parse(command, data)
            timestamp = int(time.time())
            event = Event(command, parsed_data, timestamp)
            event.description = self._describe(event)

            for storage in self._storage:
                storage.store(event)

            for notifier in self._notifiers:
                try:
                    notifier.notify(event)
                except Exception as e:
                    # TODO: Implement better error handling/logging
                    print("Error notifying on {name}: {exception}".format(name=notifier, exception=e))
