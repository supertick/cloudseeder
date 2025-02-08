from .local import LocalQueue
from .sqs import SQSQueue
from .azure import AzureQueueClient
from .noop import NoOpQueue

# Singleton dictionary to store named queue instances
_queues = {}

def get_queue_client(name: str, queue_type="local", **kwargs):
    """
    Retrieves a queue client instance. If a queue with the same name already exists, returns the existing instance.
    
    :param name: The unique name of the queue instance.
    :param queue_type: Type of queue to create (local, sqs, azure, noop).
    :param kwargs: Additional arguments for queue initialization.
    :return: A singleton instance of the requested queue.
    """
    if name in _queues:
        return _queues[name]

    # Create a new queue instance if it doesn't exist
    if queue_type == "noop":
        queue_instance = NoOpQueue()
    elif queue_type == "local":
        queue_instance = LocalQueue()
    elif queue_type == "sqs":
        queue_instance = SQSQueue(name, kwargs["aws_access_key_id"], kwargs["aws_secret_access_key"])
    elif queue_type == "azure":
        queue_instance = AzureQueueClient(kwargs["connection_string"], kwargs["queue_name"])
    else:
        raise ValueError(f"Invalid queue type: {queue_type}")

    # MQTT queue ?
    # ROS2 queue ?

    # Store the instance in the singleton dictionary
    _queues[name] = queue_instance
    return queue_instance
