import queue
from .interface import QueueClient

class NoOpQueue(QueueClient):
    def __init__(self):
        pass

    def send_message(self, message: str):
        pass

    def receive_message(self):
        pass

    def delete_message(self, message_id):
        pass
