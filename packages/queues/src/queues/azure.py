from azure.storage.queue import QueueClient as AzureQueue
from .base import QueueClient

class AzureQueueClient(QueueClient):
    def __init__(self, connection_string, queue_name):
        self.client = AzureQueue.from_connection_string(connection_string, queue_name)

    def send_message(self, message: str):
        self.client.send_message(message)

    def receive_message(self):
        messages = self.client.receive_messages()
        return next(iter(messages), None)

    def delete_message(self, message_id):
        self.client.delete_message(message_id)
