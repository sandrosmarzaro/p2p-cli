import socket
import _thread
import os
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
        self.IP = self.__try_get_ip()
        self.ID = hash(self.IP)

    def __try_get_ip(self):
        global ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith("127."):
                s.connect(("1.1.1.1", 80))
                ip = s.getsockname()[0]
            if ip is None:
                raise Exception("IP not found")
        except:
            ip = "127.0.0.1"
        finally:
            s.close()
            return ip


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


if __name__ == "__main__":
    main()
