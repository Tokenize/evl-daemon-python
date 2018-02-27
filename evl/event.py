import logging
import time

from datetime import datetime

import evl.command as cmd
import evl.data as dt

logger = logging.getLogger(__name__)


class Event:
    """
    Represents an event from the EVL module, including the command, data,
    priority, timestamp and string description of the event.
    """

    def __init__(self, command: cmd.Command, data: dict, timestamp=None):
        self.command = command

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
        return EventManager.zones.get(self.zone, "Zone {zone}".format(
            zone=self.zone))

    def partition_name(self) -> str:
        if self.partition is None:
            return ""
        return EventManager.partitions.get(self.partition,
                                           "Partition {partition}".format(partition=self.partition))

    def describe(self) -> str:
        """
        Describes the event based on its command and data.
        :return: Description of event
        """
        cmd_desc = self.command.describe()
        command_type = self.command.command_type

        # Specific command types
        if command_type in (cmd.CommandType.KEYPAD_LED_FLASH_STATE, cmd.CommandType.KEYPAD_LED_STATE):
            led_state = dt.describe_led_state(self.data)
            description = "{command}: {state}".format(
                command=cmd_desc,
                state=led_state)
        elif command_type in cmd.LOGIN_COMMANDS:
            login_type = dt.LoginType(self.data)
            description = "{command}: {login}".format(
                command=cmd_desc,
                login=dt.LOGIN_TYPE_NAMES[login_type])
        elif command_type == cmd.CommandType.PARTITION_ARMED:
            armed_type = dt.PartitionArmedType(self.data)
            armed_name = dt.PARTITION_ARMED_NAMES[armed_type]

            description = "{command} ({armed_name}): [{partition}]".format(
                command=cmd_desc,
                partition=self.partition_name(),
                armed_name=armed_name
            )

        # General command types
        elif command_type in cmd.PARTITION_COMMANDS:
            description = "{command}: [{partition}]".format(
                command=cmd_desc,
                partition=self.partition_name())
        elif command_type in cmd.PARTITION_AND_ZONE_COMMANDS:
            description = "{command}: [{partition}] {zone}".format(
                command=cmd_desc,
                partition=self.partition_name(),
                zone=self.zone_name())
        elif command_type in cmd.ZONE_COMMANDS:
            description = "{command}: {zone}".format(
                command=cmd_desc,
                zone=self.zone_name())
        else:
            description = "{command}".format(command=cmd_desc)

        return description

    def timestamp_str(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))

    def __str__(self) -> str:
        return self.describe()


class Status:
    """
    Represents the current status of the device, partitions, zones, connection,
    etc.
    """

    def __init__(self):
        self.started_at = datetime.now()
        self.notifiers = []
        self.storage = []
        self.listeners = []

        self.armed_state = {}

        self.partitions = {}
        self.zones = {}

        self.last_event = None

        self.connection = {'hostname': '', 'port': 0}

    def update(self, event: Event):
        if event.partition:
            self.partitions[event.partition] = event.describe()

        if event.zone:
            self.zones[event.zone] = event.describe()

        command_type = event.command.command_type
        if command_type in (cmd.CommandType.PARTITION_DISARMED,
                            cmd.CommandType.PARTITION_ARMED):
            self.armed_state[event.partition] = event.describe()

        self.last_event = event

    def report(self) -> dict:
        uptime = datetime.now() - self.started_at

        last_event = ''
        if self.last_event:
            last_event = "[{timestamp}] {description}".format(
                timestamp=self.last_event.timestamp_str(),
                description=self.last_event.describe())

        return {
            'uptime': uptime.total_seconds(),
            'armed_state': self.armed_state,
            'partitions': self.partitions,
            'zones': self.zones,
            'notifiers': [str(n) for n in self.notifiers],
            'storage': [str(s) for s in self.storage],
            'listeners': [str(l) for l in self.listeners],
            'connection': self.connection,
            'last_event': last_event
        }


class EventManager:
    """
    Represents an event manager that waits for incoming events from an event queue
    and dispatches events to its list of event notifiers.
    """

    partitions = {}
    zones = {}

    def __init__(self, event_queue, queue_group=None, notifiers: list=None, storage: list=None, status: Status=None):

        if notifiers is None:
            notifiers = []
        self._notifiers = notifiers

        if storage is None:
            storage = []
        self._storage = storage

        if status is None:
            status = Status()

        self.status = status
        self.status.notifiers = self._notifiers
        self.status.storage = self._storage

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

    def enqueue(self, command: cmd.Command, data: str = ""):
        self._event_queue.put((command, data))

    def status_report(self):
        return self.status.report()

    def wait(self):
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = self._event_queue.get()
            parsed_data = dt.parse(command, data)
            timestamp = int(time.time())
            event = Event(command, parsed_data, timestamp)

            self.status.update(event)

            for storage in self._storage:
                storage.store(event)

            for notifier in self._notifiers:
                try:
                    notifier.notify(event)
                except Exception as e:
                    logger.error("Error notifying on {name}: {exception}".format(
                        name=notifier, exception=e))
