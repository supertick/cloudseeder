from queues.local import LocalQueue

def test_local_queue():
    queue = LocalQueue()
    queue.send_message("test")
    assert queue.receive_message() == "test"
