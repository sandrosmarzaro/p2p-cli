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
    def __init__(self, ip, name):
        self.PORT = 12345
        self.IP = ip
        self.NAME = name
        self.ID = hash(self.IP + self.NAME)
        self.previous = {}
        self.next = {}


class P2P:
    def __init__(self, ip, name):
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.NODE = Node(ip, name)
        self.LISTENER = _thread.start_new_thread(self.listener, ())
        self.menu()

    def listener(self):
        orig = ("", self.NODE.PORT)
        self.SOCKET.bind(orig)
        logging.info(f"Node {self.NODE.ID} - {self.NODE.NAME} listening on {self.NODE.IP}:{self.NODE.PORT}")
        while True:
            msg, client = self.SOCKET.recvfrom(1024)
            msg_decoded = msg.decode("utf-8")
            logging.debug(f"Message received: {msg_decoded}")
            string_dict = json.loads(msg_decoded)
            if string_dict["codigo"] == 0:
                pass
            elif string_dict["codigo"] == 1:
                pass
            elif string_dict["codigo"] == 2:
                self.lookup_response(string_dict)
            elif string_dict["codigo"] == 3:
                pass
            elif string_dict["codigo"] == 64:
                pass
            elif string_dict["codigo"] == 65:
                pass
            elif string_dict["codigo"] == 66:
                self.lookup_control(string_dict)
            elif string_dict["codigo"] == 67:
                pass

    def menu(self):
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
                self.create_network()
            elif option == 2:
                self.join_network()
            elif option == 3:
                self.leave_network()
            elif option == 4:
                self.node_info()
            elif option == 0:
                self.exit_program()
            else:
                invalid_option()

    def create_network(self):
        self.NODE.previous.update({"id": self.NODE.ID, "ip": self.NODE.IP})
        self.NODE.next.update({"id": self.NODE.ID, "ip": self.NODE.IP})
        clear_console()
        print_lines(50)
        print("Network Created!")
        print_lines(50)
        input("Press enter to continue...")
        logging.debug(f"Network Created - Node IP: {self.NODE.IP}, NAME: {self.NODE.NAME}, PORT: {self.NODE.PORT}, "
                      f"ID: {self.NODE.ID}, previous: {self.NODE.previous}, next: {self.NODE.next}")

    def join_network(self):
        clear_console()
        print_lines(50)
        print("Enter the IP of the node you want to join")
        print_lines(50)
        ip = input("IP: ")
        self.lookup_request(ip)

    def leave_network(self):
        pass

    def lookup_request(self, ip):
        msg_lookup = {
            "codigo": 2,
            "identificador": self.NODE.ID,
            "ip_origem_busca": self.NODE.IP,
            "id_busca": self.NODE.ID
        }
        msg_lookup_json = json.dumps(msg_lookup)
        msg_lookup_encoded = msg_lookup_json.encode("utf-8")
        logging.debug(f"Sent Lookup Request to {ip} - {msg_lookup_encoded}")
        self.SOCKET.sendto(msg_lookup_encoded, (ip, self.NODE.PORT))

    def lookup_response(self, request_dict):
        response_dict = {
            "codigo": 66,
            "id_busca": self.NODE.ID,
            "id_origem": request_dict["identificador"],
            "ip_origem": request_dict["ip_origem_busca"],
            "id_antecessor": self.NODE.previous["id"],
            "ip_antecessor": self.NODE.previous["ip"],
            "id_sucessor": self.NODE.next["id"],
            "ip_sucessor": self.NODE.next["ip"]
        }
        response_json = json.dumps(response_dict)
        response_encoded = response_json.encode("utf-8")
        logging.debug(f"Sent Lookup Response Message - {response_encoded}")
        self.SOCKET.sendto(response_encoded, (request_dict["ip_origem_busca"], self.NODE.PORT))

    def lookup_control(self, request_dict):
        request_id = request_dict["identificador"]
        concurrent_id = self.NODE.ID
        next_id = self.NODE.next["id"]
        previous_id = self.NODE.previous["id"]

        if request_id == concurrent_id:
            # Error message, ambiguous ID
            ambiguous_id_error()
        elif request_id > concurrent_id:
            # Inset in the end              Insert in the middle
            if next_id <= concurrent_id or next_id > request_id:
                self.join_request(self.NODE.IP)
            else:
                # Keep going forward
                self.lookup_request(self.NODE.next["ip"])
        elif request_id < concurrent_id:
            # Insert in the beginning           Insert in the middle
            if previous_id >= concurrent_id or previous_id < request_id:
                self.join_request(self.NODE.IP)
            else:
                # Keep going backwards
                self.lookup_request(self.NODE.previous["ip"])
                pass

    def join_request(self, ip):
        string_dict = {
            "codigo": 0,
            "id": self.NODE.ID,
            "ip": self.NODE.IP
        }
        json_dict = json.dumps(string_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Join Request Message to {ip} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (ip, self.NODE.PORT))

    def update(self):
        pass

    def node_info(self):
        clear_console()
        print_lines(50)
        print(f"Port: {self.NODE.PORT}")
        print(f"IP: {self.NODE.IP}")
        print(f"Name: {self.NODE.NAME}")
        print(f"ID: {self.NODE.ID}")
        print(f"Previous: {self.NODE.previous}")
        print(f"Next: {self.NODE.next}")
        print_lines(50)
        input("Press enter to continue...")

    def exit_program(self):
        clear_console()
        print_lines(50)
        print("Exiting...")
        self.leave_network()
        print_lines(50)
        input("Press enter to continue...")
        clear_console()
        logging.debug(f"Node {self.NODE.ID} exited")
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


def ambiguous_id_error():
    clear_console()
    print_lines(50)
    print("Error: Ambiguous ID!")
    print_lines(50)
    input("Press enter to continue...")
    clear_console()
    exit(0)


def main():
    if len(sys.argv) != 3:
        clear_console()
        print("Invalid arguments! Usage: python3 node.py <IP> <NAME>")
        exit(0)
    P2P(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
