import logging
import time

from datetime import datetime

import evl.command as cmd
import evl.data as dt
import evl.util as util

logger = logging.getLogger(__name__)


class Event:
    """
    Represents an event from the EVL module, including the command, data,
    priority, timestamp and string description of the event.
    """

    def __init__(self, command: cmd.Command, data: dict, timestamp=None):
        self.command = command

        self.data = data.get("data", None)
        self.zone = data.get("zone", None)
        self.partition = data.get("partition", None)

        self.priority = cmd.PRIORITIES.get(command.command_type, cmd.Priority.LOW)

        if timestamp is None:
            timestamp = int(time.time())
        self.timestamp = timestamp

    def zone_name(self) -> str:
        """
        Returns the zone name associated with this event, if applicable.
        :return: Zone name
        """

        if self.zone is None:
            return ""
        return EventManager.zones.get(self.zone, "Zone {zone}".format(zone=self.zone))

    def partition_name(self) -> str:
        """
        Returns the partition name associated with this event, if applicable.
        :return: Partition name
        """

        if self.partition is None:
            return ""
        return EventManager.partitions.get(
            self.partition, "Partition {partition}".format(partition=self.partition)
        )

    def describe(self) -> str:
        """
        Describes the event based on its command and data.
        :return: Description of event
        """

        cmd_desc = self.command.describe()
        description = "{command}: {data}".format(
            command=cmd_desc, data=self.describe_data()
        )

        return description

    def describe_data(self) -> str:
        """
        Describes the event data based on command type.
        :return: Description of command data
        """

        command_type = self.command.command_type
        if command_type in (
            cmd.CommandType.KEYPAD_LED_FLASH_STATE,
            cmd.CommandType.KEYPAD_LED_STATE,
        ):
            return dt.describe_led_state(self.data)

        elif command_type in cmd.LOGIN_COMMANDS:
            login_type = dt.LoginType(self.data)
            return dt.LOGIN_TYPE_NAMES[login_type]

        elif command_type == cmd.CommandType.PARTITION_ARMED:
            armed_type = dt.PartitionArmedType(self.data)
            armed_name = dt.PARTITION_ARMED_NAMES[armed_type]
            return "({armed_name}: [{partition}]".format(
                armed_name=armed_name, partition=self.partition_name()
            )

        # General command types
        elif command_type in cmd.PARTITION_COMMANDS:
            return self.partition_name()

        elif command_type in cmd.PARTITION_AND_ZONE_COMMANDS:
            return "[{partition}] {zone}".format(
                partition=self.partition_name(), zone=self.zone_name()
            )

        elif command_type in cmd.ZONE_COMMANDS:
            return self.zone_name()

        else:
            return ""

    def timestamp_str(self) -> str:
        """
        Returns a formatted date of the event's timestamp.
        :return: Formatted date string
        """

        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))

    def __str__(self) -> str:
        """
        Returns a description of the event.
        :return: Description of event
        """

        return self.describe()


class Status:
    """
    Represents the current status of the device, partitions, zones, connection,
    etc.
    """

    def __init__(self):
        self.started_at = datetime.now()
        self.notifiers = {}
        self.storage = {}
        self.listeners = []

        self.armed_state = {}

        self.partitions = {}
        self.zones = {}

        self.last_event = None

        self.connection = {"hostname": "", "port": 0}

    def update(self, event: Event) -> None:
        """
        Updates the status of the system with the details from the given event.
        :param event: Event to be used to update status
        """

        if event.partition:
            self.partitions[event.partition] = event.describe()

        if event.zone:
            self.zones[event.zone] = event.describe()

        command_type = event.command.command_type
        if command_type in (
            cmd.CommandType.PARTITION_DISARMED,
            cmd.CommandType.PARTITION_ARMED,
        ):
            self.armed_state[event.partition] = event.describe()

        self.last_event = event

    def report(self) -> dict:
        """
        Returns a dict containing various system status details.
        :return: Dict of system status details
        """

        uptime = datetime.now() - self.started_at

        last_event = ""
        if self.last_event:
            last_event = "[{timestamp}] {description}".format(
                timestamp=self.last_event.timestamp_str(),
                description=self.last_event.describe(),
            )

        return {
            "statuses": {"zones": self.zones, "partitions": self.partitions},
            "armed_state": self.armed_state,
            "connection": self.connection,
            "last_event": last_event,
            "listeners": [str(listener) for listener in self.listeners],
            "notifiers": [str(n) for _, n in self.notifiers.items()],
            "partitions": util.describe_dict(EventManager.partitions),
            "storage": [str(s) for _, s in self.storage.items()],
            "uptime": uptime.total_seconds(),
            "zones": util.describe_dict(EventManager.zones),
        }


class EventManager:
    """
    Represents an event manager that waits for incoming events from an event
    queue and dispatches events to its list of event notifiers.
    """

    partitions = {}
    zones = {}

    def __init__(
        self,
        event_queue,
        notifiers: dict = None,
        storage: dict = None,
        status: Status = None,
    ):

        if notifiers is None:
            notifiers = {}
        self._notifiers = notifiers

        if storage is None:
            storage = {}
        self.storage = storage

        if status is None:
            status = Status()

        self.status = status
        self.status.notifiers = self._notifiers
        self.status.storage = self.storage

        self._event_queue = event_queue

    def add_notifiers(self, notifiers: dict) -> None:
        """
        Adds a dictionary of notifiers to the existing dictionary.
        :param notifiers: Dictionary of notifiers to add to notifier dictionary
        """
        self._notifiers = util.merge_dicts(self._notifiers, notifiers)
        self.status.notifiers = self._notifiers

    def remove_notifier(self, name: str) -> None:
        """
        Removes the notifier with the given name from the list of active
        notifiers.
        :param name: Name of notifier to remove
        """
        self._notifiers.pop(name, None)

    def add_storages(self, storages: dict) -> None:
        """
        Adds a dictionary of storages to the existing dictionary.
        :param storages: Dictionary of storages to add to storage dictionary
        """
        self.storage = util.merge_dicts(self.storage, storages)
        self.status.storage = self.storage

    async def enqueue(self, command: cmd.Command, data: str = "") -> None:
        """
        Adds the given command and data to the event queue to be processed.
        :param command: Command to add to the event queue
        :param data: Data to add to the event queue with the given command
        """
        await self._event_queue.put((command, data))

    def status_report(self) -> dict:
        """Returns the current status report of the system."""
        return self.status.report()

    async def wait(self) -> None:
        """Initiate wait for incoming events in event queue."""
        while True:
            (command, data) = await self._event_queue.get()
            parsed_data = dt.parse(command, data)
            timestamp = int(time.time())
            event = Event(command, parsed_data, timestamp)

            self.status.update(event)

            for storage_key in list(self.storage):
                storage = self.storage.get(storage_key, None)
                if storage:
                    storage.store(event)

            for notifier_key in list(self._notifiers):
                notifier = self._notifiers.get(notifier_key, None)
                if notifier:
                    try:
                        await notifier.notify(event)
                    except Exception as e:
                        logger.error(
                            "Error notifying on {name}: {exception}".format(
                                name=notifier, exception=e
                            )
                        )
