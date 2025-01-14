import boto3
from .interface import QueueClient

class SQSQueue(QueueClient):
    def __init__(self, queue_url):
        self.client = boto3.client("sqs")
        self.queue_url = queue_url

    def send_message(self, message: str):
        self.client.send_message(QueueUrl=self.queue_url, MessageBody=message)

    def receive_message(self):
        response = self.client.receive_message(QueueUrl=self.queue_url, MaxNumberOfMessages=1)
        messages = response.get("Messages", [])
        return messages[0] if messages else None

    def delete_message(self, message_id):
        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message_id)
