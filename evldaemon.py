import sys

from gevent import socket
import gevent.pool
import gevent.queue
import tpi


class Connection:

    def __init__(self, host, port=4025, password=""):
        self.host = host
        self.port = port
        self.password = password

        self._recv_queue = gevent.queue.Queue()
        self._send_queue = gevent.queue.Queue()
        self._ack_queue = gevent.queue.Queue()
        self._group = gevent.pool.Group()
        self._conn = None

    def start(self):
        self._group.spawn(self.connect)
        self._group.spawn(self._process_loop)
        self._group.spawn(self._send_loop)
        self._group.join()

    def connect(self):
        print("Connecting to EVL...")
        self._conn = socket.create_connection((self.host, self.port))

        while True:
            data = self._conn.recv(512)

            if not data:
                break

            data_str = data.decode("ascii").strip()
            events = data_str.split("\r\n")

            for e in events:
                self._recv_queue.put(e)

        print("Disconnected!")
        self.stop()

    def _send_loop(self):
        while True:
            command = self._send_queue.get()
            self._conn.sendall(command.encode())

    def _process_loop(self):
        print("Listening for events..")
        
        while True:
            event = self._recv_queue.get()

            if tpi.command(event) == "505" and tpi.data(event) == "3":
                print("Logging in...")
                self.send("005", self.password)
            else:
                print("Event: {0}".format(event))

    def stop(self):
        print("Killing processes..")

        if self._conn is not None:
            self._conn.close()

        self._group.kill()

    def send(self, command, data=""):
        checksum = tpi.calculate_checksum(command + data)
        packet = command + data + checksum + "\r\n"
        self._send_queue.put(packet)

        # TODO: Wait on ack queue for acknowledgement (with timeout?)

if __name__ == '__main__':
    print("Welcome to EvlDaemon")

    if len(sys.argv) < 3:
        print("Usage: evldaemon.py <host> <password>")
        sys.exit()

    host = sys.argv[1]
    password = sys.argv[2]

    connection = Connection(host=host, password=password)
    connection.start()
