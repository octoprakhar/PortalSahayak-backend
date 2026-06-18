from queue import Queue

from all_models.Message import Message

class Mailbox:
    """
    Each worker will have it's own mail box. in which it has it's own message id.
    We need to use worker id somewhere. And also use ActiveJobStore for that, we need to 
    modify it to store all the currently working workers
    """
    def __init__(self):
        self._queue = Queue()

    def push(self, message: Message):
        self._queue.put(message)

    def receive(self) -> Message:
        return self._queue.get()