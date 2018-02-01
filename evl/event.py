import time

import evl.command as cmd
import evl.data as dt


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

        self.priority = cmd.PRIORITIES.get(command.command_type, cmd.Priority.LOW)

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
        :param storages: Storage engine to add to storage list
        """
        self._storage.extend(storages)

    def _describe(self, event: Event) -> str:
        """
        Describes the given event based on the event's command and data.
        :param event: Event to describe
        :return: Description of event
        """
        cmd_desc = event.command.describe()
        command_type = event.command.command_type
        if command_type in cmd.LOGIN_COMMANDS:
            login_type = dt.LoginType(event.data)
            description = "{command}: {login}".format(command=cmd_desc,
                                                      login=dt.LOGIN_TYPE_NAMES[login_type])
        elif command_type in cmd.PARTITION_COMMANDS:
            description = "{command}: [{partition}]".format(command=cmd_desc, partition=event.partition_name())
        elif command_type in cmd.PARTITION_AND_ZONE_COMMANDS:
            description = "{command}: [{partition}] {zone}".format(command=cmd_desc,
                                                                   partition=event.partition_name(),
                                                                   zone=event.zone_name())
        elif command_type in cmd.ZONE_COMMANDS:
            description = "{command}: {zone}".format(command=cmd_desc, zone=event.zone_name())
        elif command_type in (cmd.CommandType.KEYPAD_LED_FLASH_STATE, cmd.CommandType.KEYPAD_LED_STATE):
            led_state = dt.describe_led_state(event.data)
            description = "{command}: {state}".format(command=cmd_desc, state=led_state)
        else:
            description = "{command}".format(command=cmd_desc)
        return description

    def enqueue(self, command: cmd.Command, data: str = ""):
        self._event_queue.put((command, data))

    def wait(self):
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = self._event_queue.get()
            parsed_data = dt.parse(command, data)
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
