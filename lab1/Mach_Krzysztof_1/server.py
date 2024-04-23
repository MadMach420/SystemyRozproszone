import socket
from threading import Thread

from message import Message


class Server:
    def __init__(self):
        self.address = "127.0.0.1"
        self.port = 9008
        self.clients = {}

    def start(self):
        Thread(target=self.udp_messages, args=()).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.port))
            print('Server started')
            self.accept_connections(s)

    def udp_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.address, self.port))
            while True:
                data, sender_address = s.recvfrom(10240)
                self.handle_message(Message.from_bytearray(data))

    def accept_connections(self, s):
        while True:
            s.listen()
            connection, address = s.accept()
            Thread(target=self.handle_connection, args=(connection, )).start()

    def handle_connection(self, connection):
        with connection:
            client = self.init_connection(connection)
            if client:
                print(f'Connection started with {client}')
                while True:
                    data = connection.recv(10240)
                    if not data:
                        del self.clients[client]
                        break
                    message: Message = Message.from_bytearray(data)
                    self.handle_message(message)

    def handle_message(self, message: Message):
        for user, connection in self.clients.items():
            if user != message.sender:
                connection.send(bytes(message))

    def init_connection(self, connection):
        init_data = connection.recv(10240)
        init_message: Message = Message.from_bytearray(init_data)
        if init_message.sender in self.clients.keys():
            response = Message("Name already taken", Message.END_CONNECTION)
            connection.send(bytes(response))
            return ''
        else:
            self.clients[init_message.sender] = connection
            return init_message.sender


if __name__ == '__main__':
    Server().start()
