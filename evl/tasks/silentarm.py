import logging

import evl.event as ev
import evl.command as cmd

logger = logging.getLogger(__name__)


class SilentArmTask:
    """
    A task that sends a Software Zone Alarm command when a Zone Open
    command occurs on a given zone.
    """

    def __init__(self, event_manager: ev.EventManager, partitions: list, zones: list):
        self.event_manager = event_manager
        self.partitions = partitions
        self.zones = zones

        self.alarm_triggers = (cmd.CommandType.ZONE_OPEN,)
        self.shutdown_triggers = (
            cmd.CommandType.PARTITION_ARMED,
            cmd.CommandType.SYSTEM_ARMING_IN_PROGRESS,
        )

    def __str__(self):
        return "Silent Arm Task"

    def start(self) -> None:
        """
        Starts the silent alarm task by adding itself to the event manager's
        list of notifiers.
        """
        logger.debug("Starting silent-arm task")
        self.event_manager.add_notifiers({"silent-arm": self})

    def stop(self) -> None:
        """
        Stops the silent alarm task by removing itself from the event manager's
        list of notifiers.
        """
        logger.debug("Stopping silent arm task")
        self.event_manager.remove_notifier("silent-arm")

    async def notify(self, event: ev.Event) -> None:
        """
        Event notifier that triggers an alarm if the given event is in the
        list of alarm triggers or shuts down the silent alarm task if the event
        is in the list of shutdown triggers.
        :param event: Event sent from EVL device
        """
        if event.command.command_type in self.alarm_triggers:
            await self._alarm(event)
        elif event.command.command_type in self.shutdown_triggers:
            self._shutdown(event)

    async def _alarm(self, event: ev.Event) -> None:
        """
        Sends a Software Zone Alarm event to the event manager queue if the
        given event zone is in the list of alarm zones.
        :param event: Event sent from EVL device
        """
        if event.zone not in self.zones:
            return
        if event.partition is not None and event.partition not in self.partitions:
            return

        logger.debug("Silent alarm task triggered")
        command = cmd.Command(cmd.CommandType.SOFTWARE_ZONE_ALARM.value)
        data = "{zone}".format(zone=event.zone)
        await self.event_manager.enqueue(command, data)

    def _shutdown(self, event: ev.Event) -> None:
        """
        Removes the silent arm notifier when a shutdown event is received.
        """
        if event.partition not in self.partitions:
            return

        self.stop()
