import gevent.pool
import gevent.queue
from gevent import socket
import logging

import evl.tpi as tpi
import evl.command as cmd
import evl.data as dt
import evl.event as ev

logger = logging.getLogger(__name__)


class Connection:
    """
    Represents a connection to an EVL device. Responsible for connecting to the
    EVL, sending and receiving data, and processing incoming commands as
    appropriate.
    """
    def __init__(self, event_manager: ev.EventManager,
                 queue_group: gevent.pool.Group, host: str, port: int=4025,
                 password: str=""):

        self.host = host
        self.port = port
        self.password = password

        self._event_manager = event_manager
        self._queue_group = queue_group

        self._recv_queue = gevent.queue.Queue()
        self._send_queue = gevent.queue.Queue()
        self._ack_queue = gevent.queue.Queue()

        self._conn = None

    def start(self):
        """
        Begins processing by connecting to the EVL device and initiating
        the various data handling routines.
        """
        self._connect()

        self._queue_group.spawn(self._receive)
        self._queue_group.spawn(self._send)
        self._queue_group.spawn(self._process)

    def _connect(self):
        """Initiates connection to the EVL device."""
        logger.debug("Connecting to EVL...")
        self._conn = socket.create_connection((self.host, self.port))

    def _receive(self):
        """
        Receive loop that accepts incoming data from the EVL device,
        decodes it and adds it to the receive queue for processing.
        """
        incomplete = ""
        while True:
            try:
                data = self._conn.recv(512)
            except IOError:
                data = None

            if not data:
                break

            decoded = incomplete + data.decode("ascii")
            if decoded.endswith("\r\n"):
                # Complete command(s) received
                events = decoded.strip().split("\r\n")
                incomplete = ""
            else:
                # Incomplete command received
                split = decoded.split("\r\n")
                events = split[:-1]
                incomplete = split[-1]

            for e in events:
                self._recv_queue.put(e)

        logger.warning("Disconnected!")
        self.stop()

    def _send(self):
        """
        Send loop that sends outgoing commands to the EVL device and waits
        for the corresponding acknowledgement to be received.
        """
        while True:
            packet = self._send_queue.get()
            self._conn.sendall(packet.encode())

            try:
                ack = self._ack_queue.get(timeout=2)
                if tpi.parse_data(ack) != tpi.parse_command(packet):
                    logger.error("Incorrect acknowledgement!")
            except gevent.queue.Empty:
                logger.error("Timeout waiting for acknowledgement!")

    def _process(self):
        """
        Processing loop that receives incoming commands and processes as
        necessary.
        """
        while True:
            event = self._recv_queue.get()

            command = cmd.Command(tpi.parse_command(event))
            data = tpi.parse_data(event)
            if command.command_type == cmd.CommandType.LOGIN and dt.LoginType(data) == dt.LoginType.PASSWORD_REQUEST:
                logger.debug("Logging in...")
                self.send(cmd.CommandType.NETWORK_LOGIN, self.password)
            elif command.command_type == cmd.CommandType.COMMAND_ACKNOWLEDGE:
                self._ack_queue.put(event)
            else:
                self._event_manager.enqueue(command, data)

    def stop(self):
        """Cleanly stop all processing and disconnect from the EVL device."""
        if self._conn is not None:
            self._conn.close()

    def send(self, command: cmd.CommandType, data: str= ""):
        """
        Send the given command and data to the EVL device.
        :param command: CommandType to send
        :param data: Data to send, if applicable
        """
        command_str = command.value
        checksum = tpi.calculate_checksum(command_str + data)
        packet = "{command}{data}{checksum}\r\n".format(
            command=command_str,
            data=data,
            checksum=checksum)
        self._send_queue.put(packet)
