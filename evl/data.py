from .command import Command, CommandType


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


def parse(command: Command, data: str) -> dict:
    parsed = {}
    command_type = command.command_type

    parsed['data'] = data
    if command_type in ZONE_COMMANDS:
        parsed['zone'] = data

    if command_type in PARTITION_COMMANDS:
        parsed['partition'] = data

    if command_type in PARTITION_AND_ZONE_COMMANDS:
        parsed['partition'] = data[:1]
        parsed['zone'] = data[1:4]

    return parsed
