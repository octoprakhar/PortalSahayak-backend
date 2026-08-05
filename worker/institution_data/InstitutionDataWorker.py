from playwright.sync_api import Page,Browser,BrowserContext,Playwright
import logging

from worker.WorkerAbstract import WorkerAbstract
from all_models.Message import Message
from constants.job_status import JobStatus
from services.RuntimeManager import RunTimeManager
from constants.Events import Events
from constants.Commands import Commands
from constants.WorkerState import WorkerState

class InstitutionDataWorker(WorkerAbstract):
    """
    The whole work of this worker is to take user data, and job metadata and returns the institution 
    list for that day and then close the browser.

    Note: It must not update jobstatus that's it.
    """

    def __init__(self, job_id, worker_context):
        super().__init__(job_id, worker_context)
        self.page: Page = None
        self.browser: Browser = None
        self.browswer_context: BrowserContext = None
        self.playwright: Playwright = None

    def _handle_institution_fetching(self, message: Message):
        """
        It will trigger Runtime Manager's launch broswer and other things till the point and returns institution data, that will
        be sent to websocket.

        """
        payload = message.payload
        planned_date = payload["planned_date"]
        
        runtimeManger = RunTimeManager(job_id=self.job_id, logger=self.log)


        runtime_job = runtimeManger.launch_browser_instance()

        self.page = runtime_job.page
        self.browser = runtime_job.browser
        self.context = runtime_job.context
        self.playwright = runtime_job.playwright
        # self._emit_event(Events.WORKER_STARTED)

        

        userName = self.worker_context.userName
        password = self.worker_context.password
        runtimeManger.login_user(self.page, userName=userName, password=password)
        # self._emit_event(Events.LOGIN_COMPLETED)



        institution_data = runtimeManger.start_select_institution_stage(page=self.page, screening_date=planned_date)
        print(f"InstitutionDataWorker: Got institution data: \n{institution_data}")
        self._emit_event(Events.INSTITUTION_FETCHED, payload=institution_data)

    def _process_command(self, message):
        if message.command == Commands.GET_INSTITUTION:
            logging.info("Got get institution command")
            self._handle_institution_fetching(message=message)
    
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