import gevent.pool
import gevent.queue
from gevent import socket

from . import tpi
from .command import Command, LoginType
from .event import EventManager


class Connection:

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
        self._connect()
        self._group.spawn(self._receive)
        self._group.spawn(self._send)
        self._group.spawn(self._process)
        self._group.spawn(self.event_manager.wait)
        self._group.join()

    def _connect(self):
        print("Connecting to EVL...")
        self._conn = socket.create_connection((self.host, self.port))

    def _receive(self):
        while True:
            data = self._conn.recv(512)

            if not data:
                break

            # TODO: Check for incomplete commands (ie. no CRLF)
            data_str = data.decode("ascii").strip()
            events = data_str.split("\r\n")

            for e in events:
                self._recv_queue.put(e)

        print("Disconnected!")
        self.stop()

    def _send(self):
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
        print("Killing processes..")

        if self._conn is not None:
            self._conn.close()

        self._group.kill()

    def send(self, command: Command, data: str=""):
        command_str = command.value
        checksum = tpi.calculate_checksum(command_str + data)
        packet = "{command}{data}{checksum}\r\n".format(command=command_str, data=data, checksum=checksum)
        self._send_queue.put(packet)
