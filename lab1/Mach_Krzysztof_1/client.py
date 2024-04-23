import os
import socket
from threading import Thread

from message import Message


class Client:
    def __init__(self):
        self.address = "127.0.0.1"
        self.port = 9008
        self.multicast_port = 9009
        self.id = input("Enter your name: ")
        self.multicast_group = input("Enter your multicast group address: ")

    def start(self):
        Thread(target=self.receive_multicast).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address, self.port))
            Thread(target=self.receive_messages, args=(s,)).start()
            self.send_messages(s)

    def read_multiline_message(self):
        message_input = input("> ")
        message_list = [message_input]
        while message_input:
            message_input = input("> ")
            message_list.append(message_input)
        return '\n'.join(message_list)

    def send_udp(self):
        message_input = self.read_multiline_message()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            message = Message(message_input, self.id)
            s.sendto(bytes(message), (self.address, self.port))

    def send_tcp(self, message_input, s):
        message = Message(message_input, self.id)
        s.send(bytes(message))

    def send_multicast(self):
        recipient = input("Enter recipient group: ")
        message_input = self.read_multiline_message()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            message = Message(message_input, self.id)
            s.sendto(bytes(message), (recipient, self.multicast_port))

    def send_messages(self, s):
        message = Message('', self.id)
        s.send(bytes(message))
        print("To send through UDP, type U, and type the message in the next lines")
        print("To send Multicast, type M")
        while True:
            message_input = input("> ")
            if message_input == 'U':
                self.send_udp()
            elif message_input == 'M':
                self.send_multicast()
            else:
                self.send_tcp(message_input, s)

    def receive_messages(self, s):
        while True:
            message = s.recv(10240)
            if not message:
                break
            message = Message.from_bytearray(message)
            if message.sender == Message.END_CONNECTION:
                print(f'Error: {message.message}')
                os._exit(1)
            else:
                print(f'\n{message.sender}:\n{message.message}\n> ', end='')

    def receive_multicast(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.multicast_group, self.multicast_port))
            while True:
                message = s.recv(10240)
                if not message:
                    break
                message = Message.from_bytearray(message)
                print(f'\n{message.sender}:\n{message.message}\n> ', end='')


if __name__ == "__main__":
    Client().start()
