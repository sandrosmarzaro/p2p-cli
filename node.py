#!/usr/sbin/python3

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
    NAME = None
    ID = None
    previous = {"id": None, "ip": None}
    next = {"id": None, "ip": None}

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
        msg_decoded = msg.decode("utf-8")
        logging.debug(f"Message received: {msg_decoded}")
        string_dict = json.loads(msg_decoded)
        if string_dict["codigo"] == 0:
            pass
        elif string_dict["codigo"] == 1:
            pass
        elif string_dict["codigo"] == 2:
            lookup_control(node, string_dict)
        elif string_dict["codigo"] == 3:
            pass
        elif string_dict["codigo"] == 64:
            pass
        elif string_dict["codigo"] == 65:
            pass
        elif string_dict["codigo"] == 66:
            pass
        elif string_dict["codigo"] == 67:
            pass


def menu(node):
    while True:
        clear_console()
        print("Select an option:")
        print_lines(50)
        print("1 - Create")
        print("2 - Join")
        print("3 - Leave")
        print("4 - Node")
        print("0 - Exit")
        print_lines(50)
        option = int(input("Option: "))
        if option == 1:
            create_network(node)
        elif option == 2:
            join_network(node)
        elif option == 3:
            leave_network(node)
        elif option == 4:
            node_info(node)
        elif option == 0:
            exit_program(node)
        else:
            invalid_option()


def create_network(node):
    node.previous = {node.ID, node.IP}
    node.next = {node.ID, node.IP}
    clear_console()
    print_lines(50)
    print("Network Created!")
    print_lines(50)
    input("Press enter to continue...")
    logging.debug(f"Network Created - Node IP: {node.IP}, NAME: {node.NAME}, PORT: {node.PORT}, ID: {node.ID}, "
                  f"previous: {node.previous}, next: {node.next}")


def join_network(node):
    clear_console()
    print_lines(50)
    print("Enter the IP of the node you want to join")
    print_lines(50)
    ip_to_join = input("IP: ")
    msg_lookup = {
        "codigo": 2,
        "identificador": node.ID,
        "ip_origem_busca": ip_to_join,
        "id_busca": node.ID
    }
    msg_lookup_json = json.dumps(msg_lookup)
    msg_lookup_encoded = msg_lookup_json.encode("utf-8")
    node.SOCKET.sendto(msg_lookup_encoded, (ip_to_join, Node.PORT))
    logging.debug(f"Sent Lookup message - {msg_lookup_encoded}")


def leave_network(node):
    pass


def lookup_control(node, dictionary):
    request_id = dictionary["identificador"]
    concurrent_id = node.ID

    if request_id == concurrent_id:
        # Error message, ambiguous ID
        pass
    elif request_id > concurrent_id:
        if node.next.id < node.ID:
            # Inset in the end
            pass
        elif node.next.id > request_id:
            # Insert in the middle
            pass
        else:
            # Keep going forward
            pass
    elif request_id < concurrent_id:
        if node.previous.id > node.ID:
            # Insert in the beginning
            pass
        elif node.previous.id < request_id:
            # Insert in the middle
            pass
        else:
            # Keep going backwards
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


def exit_program(node):
    clear_console()
    print_lines(50)
    print("Exiting...")
    leave_network(node)
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
    logging.debug(f"Node IP: {node.IP}, NAME: {node.NAME}, PORT: {node.PORT}, ID: {node.ID}, previous: {node.previous},"
                  f" next: {node.next}")
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
