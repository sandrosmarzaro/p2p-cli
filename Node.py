import socket
import _thread
import json


class Node:
    SOCKET = None
    PORT = None
    IP = None
    ID = None
    previous = None
    next = None


    def __init__(self, socket):
        self.SOCKET = socket
        self.PORT = 12345
        self.IP = self.SOCKET.gethostbyname(socket.gethostname())
        self.ID = hash(self.IP)


def listener(node):
    orig = ("", Node.PORT)
    node.SOCKET.bind(orig)
    while True:
        msg, client = node.SOCKET.recvfrom(1024)


def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    node = Node(udp)
    _thread.start_new_thread(listener(node))
    _thread.start_new_thread(cli(node, ))


def cli(node):
    pass



if __name__ == "__main__":
    main()