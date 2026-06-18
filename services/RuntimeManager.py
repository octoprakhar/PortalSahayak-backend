from playwright.sync_api import Page,sync_playwright
from typing import Callable

from constants.log_type import LogType
from all_models.RuntimeJob import RuntimeJob
from workflow.workflow import ScreeningWorkflow
from workflow.LoginPage import LoginPage
from all_models.FeedbackResult import FeedbackResult, FeedbackOutcome
from workflow.InstitutionSelectionPage import InstitutionSelectionPage
from all_models.InstitutionData import InstitutionData
from constants.log_type import LogType


class RunTimeManager:
    """
    It handles all the Runtime related things which will be stored in-memory 
    Runtime means when you had created the job, and now the browser instance is opened,
    then storing that instance, page instance, browser instance, and playwright instance for that job , in jobs/active_job.json
    Active job means the jobs which are neither IDLE, COMPLETED, FAILED.
    """

    def __init__(self, job_id: str, logger: Callable[[str,LogType],None]):
        """
        To initialize it, we need job_id, a job to Run, it must be in JobStatus.IDLE state, that means it has formed and ready to run.
        """
        self.job_id = job_id
        self.logger = logger


    def launch_browser_instance(self) -> RuntimeJob:
        """
        Only launch instance if it is in IDLE state. else throw error or other things. It will return the page instance.
        and after launching it, it must pause the screen to do the loggin thing. After launching, update the job status to JobStatus.WAITING_LOGIN
        """
        
        ## Launching the broswer instance, and then storing it in active jobs memory
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://rbsk.mohfw.gov.in/RBSK/login")

        self.logger("Browser opened and login page loaded", LogType.SUCCESS)

        return RuntimeJob(playwright=p, browser=browser, context=context,page=page)
    
    def login_user(self, page:Page, userName: str, password:str):
        """
        This will automatically login user, get userName and password from from jobMetadata
        """
        try:
            page.get_by_placeholder("Username").wait_for(
                state="visible",
                timeout=3000
            )
        except Exception as e:
            
            self.logger("Login page is not available. Please retry again or check network connection", LogType.ERROR)
            
            raise Exception(str(e))

        self.logger("Starting to log in to the portal.", LogType.SUCCESS)

        screening = page.locator('[title="Screening"]')
        loginPage = LoginPage(page=page,success_locator=screening)

        loginResult: FeedbackResult = loginPage.login(userName=userName, password=password)

        if loginResult.outcome == FeedbackOutcome.SUCCESS:

            self.logger(loginResult.message, LogType.SUCCESS)
        
            return
        
        self.logger(loginResult.message, LogType.ERROR)
        
        raise Exception(loginResult.message)

        



    def start_select_institution_stage(self, page:Page, screening_date : str) -> list[InstitutionData]:
        """
        It will help the user to open the "Select Institution" screen using month which will be of type like this "May 2026".
        Update the job status to JobStataus.WAITING_INSTITUTION
        It returns the same page instance in case it is needed again in different api request. to save it in memory. 
        I don't think in future, user will use in memory cache to give the page instance by intself when api is called, so later it may not 
        be very useful
        """

        try:
            page.locator('[title="Screening"]').wait_for(
                state="visible",
                timeout=3000
            )
        except Exception as e:
            self.logger("User is not logged in. Please login and retry.",LogType.ERROR)
            raise Exception(str(e))

        ## Verify first that user has logged in or not, if not send user an error log of failing and ask for retry

        try:
            page.locator('[title="Screening"]').click()
            page.wait_for_timeout(5000)
            institutionSelection = InstitutionSelectionPage(page=page, date=screening_date)
            resulted_institution = institutionSelection.get_month_data()

            self.logger("Waiting for user to select the intitution",LogType.INFO)
            
            return resulted_institution

        except Exception as e:
            raise RuntimeError(str(e))
        

    def start_child_screening(self, page: Page, uploaded_file_path: str, address: str, mobile_number: str, screening_date: str, institution_data: InstitutionData | None = None, is_ANM_Present: bool = True):
        """
        It will Trigger ChildScreening class to start screening, and change the job status to "RUNNING"
        
        """
        

        try:
            ##TODO: Call Get institution first because we are now in institution page so yeah....
            if institution_data:
                institutionPage = InstitutionSelectionPage(page=page, date=screening_date)
                institutionPage.select_institution(institution_data=institution_data, is_ANM_present=is_ANM_Present)
            page.get_by_role('button',name="Add New Child").wait_for(
                state="visible",
                timeout=3000
            )
        except Exception as e:
            self.logger("Institution is not selected please select the institution", LogType.ERROR)
            raise Exception(str(e))
        

        ## Start Screening Workflow with all the data
        try:
            screeningWorkFLow: ScreeningWorkflow = ScreeningWorkflow(page=page,job_id=self.job_id)
        
            failed_result = screeningWorkFLow.run(uploaded_file_path,mobile_number,address)
            ## TODO change it to csv and then send it to data
            self.logger("Completed the JOB Succesfully 🎉🎉🎉🎉.",LogType.SUCCESS)
            

        except Exception as e:
            ## Moving to failed as I can't do anything for that, user needs to retry again from start
            self.logger("Error while running the job. Please retry by closing everying.", LogType.ERROR)
            raise Exception(str(e))
        

        
            
        
        




