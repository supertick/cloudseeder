from .local import LocalQueue
from .sqs import SQSQueue
from .azure import AzureQueueClient

def get_queue_client(queue_type="local", **kwargs):
    if queue_type == "local":
        return LocalQueue()
    elif queue_type == "sqs":
        return SQSQueue(kwargs["queue_url"])
    elif queue_type == "azure":
        return AzureQueueClient(kwargs["connection_string"], kwargs["queue_name"])
    else:
        raise ValueError(f"Invalid queue type: {queue_type}")
