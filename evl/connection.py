import asyncio
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
    def __init__(self, event_manager: ev.EventManager, host: str,
                 port: int=4025, password: str=""):

        self.host = host
        self.port = port
        self.password = password

        self._event_manager = event_manager

        self._recv_queue = asyncio.Queue()
        self._send_queue = asyncio.Queue()
        self._ack_queue = asyncio.Queue()

        self._reader: asyncio.StreamReader = None
        self._writer: asyncio.StreamWriter = None

    async def start(self):
        """
        Begins processing by connecting to the EVL device and initiating
        the various data handling routines.
        """
        await self._connect()

        await asyncio.gather(
            self._receive(),
            self._send(),
            self._process()
        )

    async def _connect(self):
        """Initiates connection to the EVL device."""
        logger.debug("Connecting to EVL...")
        (self._reader, self._writer) = await asyncio.open_connection(self.host, self.port)

    async def _receive(self):
        """
        Receive loop that accepts incoming data from the EVL device,
        decodes it and adds it to the receive queue for processing.
        """
        logger.debug("Initiating receive loop...")
        incomplete = ""
        while True:
            try:
                # TODO: Refactor to use read_until()
                data = await self._reader.read(512)
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
                await self._recv_queue.put(e)

        logger.warning("Disconnected!")
        self.stop()

    async def _send(self):
        """
        Send loop that sends outgoing commands to the EVL device and waits
        for the corresponding acknowledgement to be received.
        """
        logger.debug("Initiating send loop...")
        while True:
            packet = await self._send_queue.get()
            self._writer.write(packet.encode())
            await self._writer.drain()

            try:
                ack = await asyncio.wait_for(self._ack_queue.get(), timeout=2.0)
                if tpi.parse_data(ack) != tpi.parse_command(packet):
                    logger.error("Incorrect acknowledgement!")
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for acknowledgement!")

    async def _process(self):
        """
        Processing loop that receives incoming commands and processes as
        necessary.
        """
        logger.debug("Initiating process loop...")
        while True:
            event = await self._recv_queue.get()

            if not tpi.validate_checksum(event):
                logger.error("Invalid checksum detected on incoming data!")
                continue

            command = cmd.Command(tpi.parse_command(event))
            data = tpi.parse_data(event)
            if command.command_type == cmd.CommandType.LOGIN and dt.LoginType(data) == dt.LoginType.PASSWORD_REQUEST:
                logger.debug("Logging in...")
                await self.send(cmd.CommandType.NETWORK_LOGIN, self.password)
            elif command.command_type == cmd.CommandType.COMMAND_ACKNOWLEDGE:
                await self._ack_queue.put(event)
            else:
                await self._event_manager.enqueue(command, data)

    def stop(self):
        """Cleanly stop all processing and disconnect from the EVL device."""
        if self._writer is not None:
            self._writer.close()

    async def send(self, command: cmd.CommandType, data: str= ""):
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
        await self._send_queue.put(packet)
