#!/usr/sbin/python3

import socket
import _thread
import os
import sys
import json
import logging
from traceback import print_tb

logging.basicConfig(filename='node.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


class Node:
    SOCKET = None
    PORT = None
    IP = None
    NAME = None
    ID = None
    previous = None
    next = None

    def __init__(self, udp):
        self.SOCKET = udp
        self.PORT = 12345
        self.IP = sys.argv[1]
        self.NAME = sys.argv[2]
        self.ID = hash(self.IP + self.NAME)


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
        print("1 - Join Network")
        print("2 - Leave Network")
        print("3 - Lookup Node")
        print("4 - Update Node")
        print("5 - Node Info")
        print("0 - Exit Program")
        print_lines(50)
        option = int(input("Option: "))
        if option == 1:
            join(node)
        elif option == 2:
            leave()
        elif option == 3:
            lookup()
        elif option == 4:
            update()
        elif option == 5:
            node_info(node)
        elif option == 0:
            exit_()
        else:
            invalid_option()


def join(node):
    node.previous = node.IP
    node.next = node.IP
    clear_console()
    print_lines(50)
    print("Network Created!")
    print_lines(50)
    input("Press enter to continue...")


def leave():
    pass


def lookup():
    pass


def update():
    pass


def node_info(node):
    clear_console()
    print_lines(50)
    print(f"Port: {node.PORT}")
    print(f"IP: {node.IP}")
    print(f"Name: {node.NAME}")
    print(f"ID: {node.ID}")
    print(f"Previous: {node.previous}")
    print(f"Next: {node.next}")
    print_lines(50)
    input("Press enter to continue...")


def exit_():
    clear_console()
    print_lines(50)
    print("Exiting...")
    leave()
    print_lines(50)
    input("Press enter to continue...")
    clear_console()
    exit(0)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_lines(lines):
    print("-" * lines)


def invalid_option():
    clear_console()
    print_lines(50)
    print("Invalid option!")
    print_lines(50)
    input("Press enter to continue...")


def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info("Socket created")
    node = Node(udp)
    logging.debug(f"Node IP: {node.IP}, NAME: {node.NAME}, PORT: {node.PORT}, ID: {node.ID}, previous: {node.previous}, next: {node.next}")
    _thread.start_new_thread(listener, (node,))
    menu(node)


def validate_ip():
    if len(sys.argv) != 3:
        clear_console()
        print("Invalid arguments! Usage: python3 node.py <IP> <NAME>")
        exit(1)
    main()


if __name__ == "__main__":
    validate_ip()
