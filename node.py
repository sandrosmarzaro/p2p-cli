import socket
import _thread
import os
import sys
import json
import logging

logging.basicConfig(filename='node.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


class Node:
    SOCKET = None
    PORT = None
    IP = None
    ID = None
    previous = None
    next = None

    def __init__(self, udp):
        self.SOCKET = udp
        self.PORT = 12345
        self.IP = sys.argv[1]
        self.ID = hash(self.IP)


def listener(node):
    orig = ("", Node.PORT)
    node.SOCKET.bind(orig)
    while True:
        msg, client = node.SOCKET.recvfrom(1024)


def menu(node):
    while True:
        clear_console()
        print("Select an option:")
        print_lines(50)
        print("1 - Join")
        print("2 - Leave")
        print("3 - Lookup")
        print("4 - Update")
        print("5 - Exit")
        print_lines(50)
        option = int(input("Option: "))
        switcher = {
            1: join(),
            2: leave(),
            3: lookup(),
            4: update(),
            5: exit_()
        }
        switcher.get(option, "Invalid option")


def join():
    pass


def leave():
    pass


def lookup():
    pass


def update():
    pass


def exit_():
    clear_console()
    print("Exiting...")
    leave()
    clear_console()
    exit(0)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_lines(lines):
    print("-" * lines)


def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info("Socket created")
    node = Node(udp)
    logging.debug(f"Node IP: {node.IP}, PORT: {node.PORT}, ID: {node.ID}")
    _thread.start_new_thread(listener, (node,))
    menu(node)


def validate_ip():
    if len(sys.argv) != 2:
        clear_console()
        print("Invalid arguments! Usage: python3 node.py <IP>")
        exit(1)
    main()


if __name__ == "__main__":
    validate_ip()
