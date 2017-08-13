import gevent.pool
import gevent.queue
from gevent import socket

from . import tpi
from .command import Command, LoginType
from .event import EventManager


class Connection:
    """
    Represents a connection to an EVL device. Responsible for connecting to the EVL,
    sending and receiving data, and processing incoming commands as appropriate.
    """
    def __init__(self, host: str, port: int=4025, password: str=""):
        self.host = host
        self.port = port
        self.password = password

        self._event_queue = gevent.queue.Queue()
        self.event_manager = EventManager(self._event_queue)

        self._recv_queue = gevent.queue.Queue()
        self._send_queue = gevent.queue.Queue()
        self._ack_queue = gevent.queue.Queue()
        self._group = gevent.pool.Group()
        self._conn = None

    def start(self):
        """
        Begins processing by connecting to the EVL device and initiating
        the various data handling routines.
        """
        self._connect()
        self._group.spawn(self._receive)
        self._group.spawn(self._send)
        self._group.spawn(self._process)
        self._group.spawn(self.event_manager.wait)
        self._group.join()

    def _connect(self):
        """Initiates connection to the EVL device."""
        print("Connecting to EVL...")
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

        print("Disconnected!")
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
                if tpi.data(ack) != tpi.command(packet):
                    print("Incorrect acknowledgement!")
            except gevent.queue.Empty:
                print("Timeout waiting for acknowledgement!")

    def _process(self):
        """Processing loop that receives incoming commands and processes as necessary."""
        while True:
            event = self._recv_queue.get()

            command = Command(tpi.command(event))
            data = tpi.data(event)
            if command == Command.LOGIN and LoginType(data) == LoginType.PASSWORD_REQUEST:
                print("Logging in...")
                self.send(Command.NETWORK_LOGIN, self.password)
            elif command == Command.COMMAND_ACKNOWLEDGE:
                self._ack_queue.put(event)
            else:
                self._event_queue.put((command, data))

    def stop(self):
        """Cleanly stop all processing and disconnect from the EVL device."""
        if self._conn is not None:
            self._conn.close()

        self._group.kill()

    def send(self, command: Command, data: str=""):
        """
        Send the given command and data to the EVL device.
        :param command: Command to send
        :param data: Data to send, if applicable
        """
        command_str = command.value
        checksum = tpi.calculate_checksum(command_str + data)
        packet = "{command}{data}{checksum}\r\n".format(command=command_str, data=data, checksum=checksum)
        self._send_queue.put(packet)
