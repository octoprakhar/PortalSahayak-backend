from abc import ABC,abstractmethod
from threading import Thread

from all_models.WorkerContext import WorkerContext
from worker.Mailbox import Mailbox
from worker.EventBus import EventBus
from constants.WorkerState import WorkerState
from constants.Events import Events
from all_models.WorkerEvent import WorkerEvent
from constants.log_type import LogType
from all_models.Message import Message
from constants.job_status import JobStatus

class WorkerAbstract(ABC):
    """
    This is the abstract class, with some basic intitialization each worker will need eventually, like mailbox, eventbus, workerstate, etc.
    Each worker must have at least these three things, and then start method, log method, shutdown method, process_command method, and send method.

    Note: I am not intializing playwright instances in abstract class, the reason is, suppose if a worker in future doesn't need to do anything with playwright
    then it will just be a waste. So if workers wants in future, they can initialize it by themselves. 
    """
    def __init__(self, job_id: str, worker_context:WorkerContext):
        super().__init__()
        self.job_id = job_id
        self.worker_context = worker_context
        self.running = False
        self.thread = None
        self.mail_box = Mailbox()
        self.events = EventBus()
        self.worker_state = WorkerState.CREATED
        self.job_state = JobStatus.IDLE

    def start(self):
        """
        Start the worker
        """
        if self.running:
            return
        self.worker_state = WorkerState.RUNNING
        self.running = True
        self.thread = Thread(
            target=self.run,
            daemon=True
        )
        self.thread.start()
    
    def _emit_event(self, event:Events, payload: dict = {}):
        """
        Emit the event by the worker, so that it can be consumed by the listners on EventBus
        """
        self.events.publish(WorkerEvent(event=event, job_id=self.job_id, payload=payload))
    
    def log(self, message: str, logType: LogType):
        """
        Log the progress of the worker
        """
        self._emit_event(event=Events.LOG_MESSAGE, payload={"message": message, "logType": logType})

    def send(self, message: Message):
        """
        Used by the producer, to put a new message in the mailbox of a specific worker
        """
        self.mail_box.push(message)

    @abstractmethod
    def _process_command(self,message:Message):
        """
        It will help in taking the message, and each worker can be given different commands.
        So they should process each command differently
        """
    
    def process_next_message(self):
        """
        Take the full next message of the mailbox, and then start processing the command
        """
        message = self.mail_box.receive()
        if message.job_id != self.job_id:
            raise Exception("Invalid job_id for this worker")
        self._process_command(message=message)

    def run(self):
        """
        Run the worker and process all the commands from the mail_box. And then wait and dont leave till the worker is running
        """
        while self.running:
            try:
                self.process_next_message()

            except Exception as e:
                self.job_state = JobStatus.FAILED
                self._emit_event(Events.JOB_FAILED, payload={"error":str(e)})
    
    @abstractmethod
    def shutdown(self):
        """
        It helps to clean the worker's file when worker is going to shutdown.
        """

