import sys
from evl.connection import Connection

if __name__ == '__main__':
    print("Welcome to EvlDaemon")

    if len(sys.argv) < 3:
        print("Usage: evldaemon.py <host> <password>")
        sys.exit()

    host = sys.argv[1]
    password = sys.argv[2]

    connection = Connection(host=host, password=password)
    connection.start()
