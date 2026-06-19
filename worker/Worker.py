import logging
from threading import Thread
from playwright.sync_api import Page,Browser,BrowserContext,Playwright

from worker.Mailbox import Mailbox
from constants.job_status import JobStatus
from constants.Events import Events
from all_models.Message import Message
from all_models.WorkerEvent import WorkerEvent
from constants.Commands import Commands
from constants.WorkerState import WorkerState

from services.RuntimeManager import RunTimeManager
from all_models.WorkerContext import WorkerContext
from all_models.RuntimeJob import RuntimeJob
from all_models.InstitutionData import InstitutionData
from worker.EventBus import EventBus
from constants.log_type import LogType

class Worker:
    """
    This is the main class for each worker instance.
    Worker is responsible for page, broswer, and context instaince.
    Each worker will have it's own mailbox, it emits it's own events, 
    and changes the job_state of the workflow.
    """

    def __init__(self, job_id: str, worker_context: WorkerContext):
        self.running = False
        self.thread = None
        self.job_id = job_id
        self.worker_context:WorkerContext = worker_context
        self.mail_box = Mailbox()
        self.events = EventBus()
        self.job_state = JobStatus.IDLE
        self.worker_state = WorkerState.CREATED
        self.page: Page = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.playwright: Playwright = None

    def start(self):
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
        self.events.publish(WorkerEvent(event=event, job_id=self.job_id, payload=payload))

    def _handle_create_job(self, message: Message):
        """
        It will trigger Runtime Manager's launch broswer and other things till the point and returns institution data, that will
        be sent to websocket.
        """
        if self.job_state != JobStatus.IDLE:
            raise Exception("Wrong commaind has thrown")
        
        payload = message.payload
        
        runtimeManger = RunTimeManager(job_id=self.job_id, logger=self.log)

        print(f"Job is created for id: {self.job_id}")
        runtime_job = runtimeManger.launch_browser_instance()
        self.job_state = JobStatus.STARTING
        self.page = runtime_job.page
        self.browser = runtime_job.browser
        self.context = runtime_job.context
        self.playwright = runtime_job.playwright
        self._emit_event(Events.WORKER_STARTED)

        
        self.job_state = JobStatus.LOGGING_IN
        userName = self.worker_context.userName
        password = self.worker_context.password
        runtimeManger.login_user(self.page, userName=userName, password=password)
        self._emit_event(Events.LOGIN_COMPLETED)


        self.job_state = JobStatus.WAITING_INSTITUTION
        institution_data = runtimeManger.start_select_institution_stage(page=self.page, screening_date=self.worker_context.planned_date)
        self._emit_event(Events.INSTITUTION_FETCHED, payload=institution_data)
    
    def _handle_institution_selected(self, message: Message):

        """
        Select the institution and start child screening and then prepare report
        """
        if self.job_state != JobStatus.WAITING_INSTITUTION:
            raise Exception("Wrong command has thrown")
        
        payload = message.payload
        institution_data = payload["institution_data"]
        is_ANM_Present = payload.get("is_ANM_Present", False)
        self._emit_event(event=Events.INSTITUTION_SELECTED, payload={"institution_data": institution_data})
        runtimeManager = RunTimeManager(job_id=self.job_id, logger=self.log)

        self.job_state = JobStatus.RUNNING
        uploaded_file_path = self.worker_context.uploaded_file_path
        address = self.worker_context.address
        mobile_number = self.worker_context.mobile_number
        screening_date = self.worker_context.planned_date
        runtimeManager.start_child_screening(page=self.page, institution_data=institution_data, is_ANM_Present=is_ANM_Present,screening_date=screening_date,uploaded_file_path=uploaded_file_path,address=address,mobile_number=mobile_number)
        self._emit_event(Events.REPORT_CREATED)
    
    def _process_command(self, message: Message):
        if message.command == Commands.CREATE_JOB:
            self._handle_create_job(message)

        elif message.command == Commands.INSTITUTION_SELECTED:
            self._handle_institution_selected(message)

    def process_next_message(self):
        message = self.mail_box.receive()
        if message.job_id != self.job_id:
            raise Exception("Invalid job_id for this worker")
        self._process_command(message=message)

    def log(self, message: str, logType: LogType):
        self._emit_event(event=Events.LOG_MESSAGE, payload={"message": message, "logType": logType})

    def send(self, message: Message):
        self.mail_box.push(message)

    def run(self):
        while self.running:
            try:
                self.process_next_message()

            except Exception as e:
                self.job_state = JobStatus.FAILED
                self._emit_event(Events.JOB_FAILED, payload={"error":str(e)})

    def shutdown(self):
        self.running = False
        self.worker_state = WorkerState.STOPPED

        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
