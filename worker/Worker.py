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
from all_models.RuntimeJob import RuntimeJob
from all_models.InstitutionData import InstitutionData
from worker.EventBus import EventBus

class Worker:
    """
    This is the main class for each worker instance.
    Worker is responsible for page, broswer, and context instaince.
    Each worker will have it's own mailbox, it emits it's own events, 
    and changes the job_state of the workflow.
    """

    def __init__(self, job_id: str):
        self.running = False
        self.thread = None
        self.job_id = job_id
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
        
        
        try:
            runtimeManger = RunTimeManager(job_id=self.job_id)

            print(f"Job is created for id: {self.job_id}")
            self.job_state = JobStatus.STARTING
            runtime_job = runtimeManger.launch_browser_instance()
            self.page = runtime_job.page
            self.browser = runtime_job.browser
            self.context = runtime_job.context
            self.playwright = runtime_job.playwright
            self._emit_event(Events.WORKER_STARTED)

        
            self.job_state = JobStatus.LOGGING_IN
            runtimeManger.login_user(self.page)
            self._emit_event(Events.LOGIN_COMPLETED)


            self.job_state = JobStatus.WAITING_INSTITUTION
            institution_data = runtimeManger.start_select_institution_stage(page=self.page)
            self._emit_event(Events.INSTITUTION_FETCHED, payload=institution_data)

            # print(institution_data)
        
        except Exception as e:
            self.job_state = JobStatus.FAILED
            self._emit_event(Events.JOB_FAILED, payload={"error":str(e)})
            self.shutdown()
            raise Exception(str(e))
        
    
    def _handle_institution_selected(self, message: Message):

        """
        Select the institution and start child screening and then prepare report
        """
        if self.job_state != JobStatus.WAITING_INSTITUTION:
            raise Exception("Wrong commaind has thrown")
        
        try:
            payload = message.payload
            institution_data = payload["institution_data"]
            is_ANM_Present = payload.get("is_ANM_Present", False)
            runtimeManager = RunTimeManager(job_id=self.job_id)

            # print(f"Institution got selected for id: {self.job_id}")
            self.job_state = JobStatus.COMPLETED
            runtimeManager.start_child_screening(page=self.page, institution_data=institution_data, is_ANM_Present=is_ANM_Present)
            self._emit_event(Events.REPORT_CREATED)
        except Exception as e:
            self.job_state = JobStatus.FAILED
            self._emit_event(Events.JOB_FAILED)
            raise Exception(str(e))
        finally:
            self.shutdown()

    
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

    def send(self, message: Message):
        self.mail_box.push(message)

    def run(self):
        while self.running:
            try:
                self.process_next_message()

            except Exception as e:
                logging.exception(e)
                self.job_state = JobStatus.FAILED
                self._emit_event(Events.JOB_FAILED)
                self.shutdown()

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
