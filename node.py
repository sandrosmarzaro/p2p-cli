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
    def __init__(self, ip, name, id_provided=None):
        self.PORT = 12345
        self.IP = ip
        self.NAME = name
        self.ID = self.generate_id(id_provided)
        self.previous = {}
        self.next = {}

    def generate_id(self, id_provided):
        if id_provided is None:
            return hash(self.NAME + self.IP)
        else:
            return id_provided


class P2P:
    def __init__(self, ip, name, id_provided=None):
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.NODE = Node(ip, name, id_provided)
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
                self.join_response(client[0])
            elif string_dict["codigo"] == 1:
                pass
            elif string_dict["codigo"] == 2:
                self.lookup_control(string_dict)
            elif string_dict["codigo"] == 3:
                self.update_control(string_dict, client[0])
            elif string_dict["codigo"] == 64:
                self.update_request(string_dict)
            elif string_dict["codigo"] == 65:
                pass
            elif string_dict["codigo"] == 66:
                self.join_request(string_dict, client[0])
            elif string_dict["codigo"] == 67:
                self.update_verification(string_dict, client[0])

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

    def lookup_request(self, ip_to_send, original_ip=None):
        if original_ip is None:
            original_ip = self.NODE.IP
        msg_lookup = {
            "codigo": 2,
            "identificador": self.NODE.ID,
            "ip_origem_busca": original_ip,
            "id_busca": self.NODE.ID
        }
        msg_lookup_json = json.dumps(msg_lookup)
        msg_lookup_encoded = msg_lookup_json.encode("utf-8")
        logging.debug(f"Sent Lookup Request to {ip_to_send} - {msg_lookup_encoded}")
        self.SOCKET.sendto(msg_lookup_encoded, (ip_to_send, self.NODE.PORT))

    def lookup_response(self, request_dict):
        response_dict = {
            "codigo": 66,
            "id_busca": self.NODE.ID,
            "id_origem": request_dict["identificador"],
            "ip_origem": request_dict["ip_origem_busca"],
            "id_sucessor": self.NODE.next["id"],
            "ip_sucessor": self.NODE.next["ip"]
        }
        response_json = json.dumps(response_dict)
        response_encoded = response_json.encode("utf-8")
        logging.debug(f"Sent Lookup Response Message - {response_encoded}")
        self.SOCKET.sendto(response_encoded, (request_dict["ip_origem_busca"], self.NODE.PORT))

    def lookup_control(self, request_dict):
        request_id = request_dict["identificador"]
        current_id = self.NODE.ID
        next_id = self.NODE.next["id"]
        previous_id = self.NODE.previous["id"]

        # Error message, ambiguous ID
        if request_id == current_id:
            ambiguous_id_error()
        # Only one node in the network
        elif next_id == previous_id:
            self.lookup_response(request_dict)
        # Cause the Node is the first in the network
        elif current_id < previous_id:
            # Request ID is the smallest or biggest ID in the network
            if request_id < current_id or request_id > previous_id:
                self.lookup_response(request_dict)
            # Continue the search in the network
            else:
                self.lookup_request(self.NODE.next["ip"], request_dict["ip_origem_busca"])
        # Cause the Node is in the middle of the network
        else:
            # Request ID is between the current and the previous node
            if current_id > request_id > previous_id:
                self.lookup_response(request_dict)
            # Continue the search in the network
            else:
                self.lookup_request(self.NODE.next["ip"], request_dict["ip_origem_busca"])

    def join_request(self, request_dict, ip):
        string_dict = {
            "codigo": 0,
            "id": request_dict["id_origem"],
        }
        json_dict = json.dumps(string_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Join Request Message to {ip} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (ip, self.NODE.PORT))

    def join_response(self, ip):
        response_dict = {
            "codigo": 64,
            "id_sucessor": self.NODE.ID,
            "ip_sucessor": self.NODE.ID,
            "id_antecessor": self.NODE.previous["id"],
            "ip_antecessor": self.NODE.previous["ip"]
        }
        json_dict = json.dumps(response_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Join Response Message to {ip} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (ip, self.NODE.PORT))

    def update_request(self, request_dict):
        self.NODE.previous.update({"id": request_dict["id_antecessor"], "ip": request_dict["ip_antecessor"]})
        self.NODE.next.update({"id": request_dict["id_sucessor"], "ip": request_dict["ip_sucessor"]})
        logging.debug(f"Updated Node {self.NODE.IP} - Previous: {self.NODE.previous} and next: {self.NODE.next}")
        self.update_previous_request()
        self.update_next_request()

    def update_previous_request(self):
        previous_dict = {
            "codigo": 3,
            "identificador": self.NODE.ID,
            "id_novo_antecessor": self.NODE.ID,
            "ip_novo_antecessor": self.NODE.ID
        }
        json_dict = json.dumps(previous_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Update Previous Request Message to {self.NODE.previous} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (self.NODE.previous["ip"], self.NODE.PORT))

    def update_next_request(self):
        next_dict = {
            "codigo": 3,
            "identificador": self.NODE.ID,
            "id_novo_sucessor": self.NODE.ID,
            "ip_novo_sucessor": self.NODE.ID
        }
        json_dict = json.dumps(next_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Update Next Request Message to {self.NODE.next} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (self.NODE.next["ip"], self.NODE.PORT))

    def update_control(self, request_dict, ip_to_send):
        if "id_novo_antecessor" in request_dict:
            self.NODE.previous.update({"id": request_dict["id_novo_antecessor"],
                                       "ip": request_dict["ip_novo_antecessor"]})
            logging.debug(f"Updated Node {self.NODE.IP} - Previous: {self.NODE.previous}")
        elif "id_novo_sucessor" in request_dict:
            self.NODE.next.update({"id": request_dict["id_novo_sucessor"], "ip": request_dict["ip_novo_sucessor"]})
            logging.debug(f"Updated Node {self.NODE.IP} - Next: {self.NODE.next}")
        self.update_response(ip_to_send)

    def update_response(self, ip_to_send):
        response_dict = {
            "codigo": 67,
            "id_origem_mensagem": self.NODE.ID,
        }
        json_dict = json.dumps(response_dict)
        encoded_json = json_dict.encode("utf-8")
        logging.debug(f"Sent Update Response Message to {ip_to_send} - {encoded_json}")
        self.SOCKET.sendto(encoded_json, (ip_to_send, self.NODE.PORT))

    def update_verification(self, request_dict, ip_to_send):
        logging.debug(f"Received Update Verification Message in {self.NODE.ID} from {ip_to_send} - {request_dict}")

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
    if len(sys.argv) == 3:
        P2P(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        P2P(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        clear_console()
        print_lines(50)
        print("Invalid arguments! Usage: python3 node.py <IP> <NAME> or <IP> <NAME> <ID>")
        print_lines(50)
        input("Press enter to continue...")
        exit(0)


if __name__ == "__main__":
    main()
