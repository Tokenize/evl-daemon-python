"""
Utility functions for use when working with the TPI.
"""


def calculate_checksum(cmd_data: str) -> str:
    """Calculates the checksum for the given command and data.

    Calculates the checksum for the given command and data and truncates the
    result to two bytes if necessary.

    :param cmd_data: CommandType and data to calculate checksum
    :return: Calculated checksum
    """
    checksum = sum([ord(c) for c in cmd_data])
    checksum &= 255
    return "{0:02X}".format(checksum)


def validate_checksum(packet: str) -> bool:
    """Validates the checksum provided in the given packet.

    :param packet: Data packet containing command, data and checksum
    :return: True if checksum is correct, False otherwise
    """
    cmd_data = command(packet) + data(packet)
    calculated = calculate_checksum(cmd_data)
    provided = checksum(packet)

    return calculated == provided


def checksum(packet: str) -> str:
    """Returns the checksum part of the given packet.

    :param packet: Data packet
    :return: Checksum
    """
    return packet[-2:]


def data(packet: str) -> str:
    """Returns the data part of the given packet.

    :param packet: Data packet
    :return: Data
    """
    data = ""
    if len(packet) > 5:
        data = packet[3:-2]

    return data


def command(packet: str) -> str:
    """Returns the command part of the given packet.

    :param packet: Data packet
    :return: CommandType
    """
    return packet[:3]
