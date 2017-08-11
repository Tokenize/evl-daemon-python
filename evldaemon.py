import sys
import socket

from evl.command import Priority
from evl.connection import Connection
from evl.notifiers.consolenotifier import ConsoleNotifier

if __name__ == '__main__':
    print("Welcome to EvlDaemon")

    if len(sys.argv) < 3:
        print("Usage: evldaemon.py <host> <password>")
        sys.exit()

    host = sys.argv[1]
    password = sys.argv[2]

    resolved = socket.gethostbyname(host)

    connection = Connection(host=resolved, password=password)
    console = ConsoleNotifier(priority=Priority.LOW)
    connection.event_manager.add_notifier(console)

    connection.start()
