import queue
from .base import QueueClient

class LocalQueue(QueueClient):
    def __init__(self):
        self.q = queue.Queue()

    def send_message(self, message: str):
        self.q.put(message)

    def receive_message(self):
        return self.q.get() if not self.q.empty() else None

    def delete_message(self, message_id):
        pass  # Not needed for local testing
