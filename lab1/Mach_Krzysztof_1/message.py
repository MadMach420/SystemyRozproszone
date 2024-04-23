class Message:
    END_CONNECTION = ""  # sent in self.sender by the server

    def __init__(self, message, sender):
        self.message = message
        self.sender = sender

    def __bytes__(self):
        return ';'.join([self.message, self.sender]).encode('utf-8')

    @staticmethod
    def from_bytearray(array: bytearray):
        message_str = array.decode('utf-8')
        message_array = message_str.split(';')
        return Message(message_array[0], message_array[1])
