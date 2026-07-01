from playwright.sync_api import Page,Browser,BrowserContext,Playwright

from constants.job_status import JobStatus
from constants.Events import Events
from all_models.Message import Message
from constants.Commands import Commands
from constants.WorkerState import WorkerState

from services.RuntimeManager import RunTimeManager
from services.ReportCreator import ReportCreator
from worker.WorkerAbstract import WorkerAbstract
from all_models.InstitutionData import InstitutionData

class ScreeningWorker(WorkerAbstract):
    """
    This is the class of worker helps in doing the screening by reading all the required metadata through context, and do the work
    """
    def __init__(self, job_id, worker_context):
        super().__init__(job_id, worker_context)
        self.report_creator = ReportCreator(job_id=job_id)
        self.page: Page = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.playwright: Playwright = None

    
    
    def _handle_start_screening(self, message: Message):

        """
        Select the institution and start child screening and then prepare report
        """
        if self.job_state != JobStatus.IDLE:
            raise Exception("Wrong command has thrown")
        
        payload = message.payload
        institution_data_dict = self.worker_context.institution_data
        institution_data = InstitutionData(institution_name=institution_data_dict["institution_name"], institution_plan_id=institution_data_dict["institution_plan_id"],institution_type=institution_data_dict["institution_type"],planned_date=institution_data_dict["planned_date"])
        print(f"Got type of institution data as {type(institution_data)}, and it is {institution_data}")
        if not institution_data:
            self._emit_event(event=Events.JOB_FAILED, payload={"error":"Institution data is not present"})
            raise ValueError("Institution data not present")
        is_ANM_Present = payload.get("is_ANM_Present", False)
        runtimeManger = RunTimeManager(job_id=self.job_id, logger=self.log)

        ## Step 1 launch the browser
        print(f"Job is created for id: {self.job_id}")
        runtime_job = runtimeManger.launch_browser_instance()
        self.job_state = JobStatus.STARTING
        self.page = runtime_job.page
        self.browser = runtime_job.browser
        self.context = runtime_job.context
        self.playwright = runtime_job.playwright
        self._emit_event(Events.WORKER_STARTED)

        ## Step 2 : Login to the account
        self.job_state = JobStatus.LOGGING_IN
        userName = self.worker_context.userName
        password = self.worker_context.password
        uploaded_file_path = self.worker_context.uploaded_file_path
        address = self.worker_context.address
        mobile_number = self.worker_context.mobile_number
        screening_date = self.worker_context.planned_date

        runtimeManger.login_user(self.page, userName=userName, password=password)
        self._emit_event(Events.LOGIN_COMPLETED)

        ## Step3: Just open the page, it doesn't matter whether it gives the list of institutions or not, don't emit institution fetched
        # self.job_state = JobStatus.WAITING_INSTITUTION
        # institution_data = runtimeManger.start_select_institution_stage(page=self.page, screening_date=self.worker_context.planned_date)
        runtimeManger.navigate_to_institution_page(page=self.page,screening_date=screening_date)

        ## Select the given institution.... And start screening
        # self._emit_event(event=Events.INSTITUTION_SELECTED, payload={"institution_data": institution_data})

        self.job_state = JobStatus.RUNNING
        runtimeManger.start_child_screening(page=self.page, institution_data=institution_data, is_ANM_Present=is_ANM_Present,screening_date=screening_date,uploaded_file_path=uploaded_file_path,address=address,mobile_number=mobile_number,report_creator=self.report_creator)
        success_path,failure_path = self.report_creator.flush()
        self._emit_event(Events.REPORT_CREATED,payload={"success_path": success_path,"failure_path":failure_path})
    
    def _process_command(self, message):
        if message.command == Commands.START_SCREENING:
            self._handle_start_screening(message)

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
