from playwright.sync_api import Page,sync_playwright
from typing import Callable
import re

from constants.log_type import LogType
from all_models.RuntimeJob import RuntimeJob
from workflow.workflow import ScreeningWorkflow
from workflow.LoginPage import LoginPage
from all_models.FeedbackResult import FeedbackResult, FeedbackOutcome
from workflow.InstitutionSelectionPage import InstitutionSelectionPage
from all_models.InstitutionData import InstitutionData
from constants.log_type import LogType
from services.PageSynchronizer import PageSynchronizer
from services.ReportCreator import ReportCreator
from constants.institution_type import InstitutionType


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
        self.synchronizer = PageSynchronizer()


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
        self.synchronizer.wait_loading(page=page)
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
        loginPage = LoginPage(page=page,success_locator=screening, synchronizer=self.synchronizer)

        loginResult: FeedbackResult = loginPage.login(userName=userName, password=password )

        if loginResult.outcome == FeedbackOutcome.SUCCESS:

            self.logger(loginResult.message, LogType.SUCCESS)
        
            return
        
        self.logger(loginResult.message, LogType.ERROR)
        
        raise Exception(loginResult.message)

        



    def start_select_institution_stage(self, page:Page, screening_date : str) -> list[InstitutionData] | None:
        """
        It will help the user to open the "Select Institution" screen using month which will be of type like this "May 2026".
        Update the job status to JobStataus.WAITING_INSTITUTION
        It returns the same page instance in case it is needed again in different api request. to save it in memory. 
        I don't think in future, user will use in memory cache to give the page instance by intself when api is called, so later it may not 
        be very useful
        """

        try:
            self.synchronizer.wait_loading(page=page)

            page.locator('[title="Screening"]').wait_for(
                state="visible",
                timeout=3000
            )
        except Exception as e:
            self.logger("User is not logged in. Please login and retry.",LogType.ERROR)
            return None

        ## Verify first that user has logged in or not, if not send user an error log of failing and ask for retry

        try:
            page.locator('[title="Screening"]').click()
            institutionSelection = InstitutionSelectionPage(page=page, date=screening_date, synchronizer=self.synchronizer)
            resulted_institution = institutionSelection.get_month_data()

            self.logger("Waiting for user to select the intitution",LogType.INFO)
            
            return resulted_institution

        except Exception as e:
            raise

    def navigate_to_institution_page(self,page:Page,screening_date: str) -> None:
        """
        If we are in dashboard, it will open the specific month for screening
        """
        try:
            self.synchronizer.wait_loading(page=page)

            page.locator('[title="Screening"]').wait_for(
                state="visible",
                timeout=3000
            )
        except Exception as e:
            self.logger("User is not logged in. Please login and retry.",LogType.ERROR)
            return

        ## Verify first that user has logged in or not, if not send user an error log of failing and ask for retry

        page.locator('[title="Screening"]').click()
        InstitutionSelectionPage.go_to_institution_month(page=page,synchronizer=self.synchronizer,date=screening_date)
        

    def start_child_screening(self, page: Page, uploaded_file_path: str, address: str, mobile_number: str, screening_date: str, report_creator: ReportCreator, selected_mapping: dict[str,str],max_existing_child_given:int,institution_data: InstitutionData | None = None, is_ANM_Present: bool = True):
        """
        It will Trigger ChildScreening class to start screening, and change the job status to "RUNNING"
        
        """
        

        try:
            ##TODO: Call Get institution first because we are now in institution page so yeah....
            if institution_data:
                institutionPage = InstitutionSelectionPage(page=page, date=screening_date, synchronizer=self.synchronizer)
                institutionPage.select_institution(institution_data=institution_data, is_ANM_present=is_ANM_Present)

            self.synchronizer.wait_loading(page=page)
            self.synchronizer.wait_for_all_toast_disappear(page=page)
            # print(page.get_by_text("Add New Student").count())
            button_name = (
                "Add New Child"
                if institution_data.institution_type == InstitutionType.AWC.value
                else "Add New Student"
            )
            print(f"Got institution Type as {institution_data.institution_type}")
            buttons = page.get_by_role("button", name=button_name)
            # Wait for at least one button to be visible
            buttons.first.wait_for(state="visible", timeout=3000)

            # Get the number of matching buttons
            # button_count = buttons.count()

            # print(f"Found {button_count} '{button_name}' button(s)")


            # re.compile(r"^Add New (Child|Student)$")
        except Exception as e:
            self.logger("Institution is not selected please select the institution", LogType.ERROR)
            raise
        

        ## Start Screening Workflow with all the data
        try:
            screeningWorkFLow: ScreeningWorkflow = ScreeningWorkflow(page=page,job_id=self.job_id,synchronizer=self.synchronizer,report_creator=report_creator,selected_mapping=selected_mapping, institution_type=institution_data.institution_type,max_existing_child_given=max_existing_child_given)
        
            screeningWorkFLow.run(uploaded_file_path,mobile_number,address)
            self.logger("Completed the JOB Succesfully 🎉🎉🎉🎉.",LogType.SUCCESS)
            

        except Exception as e:
            ## Moving to failed as I can't do anything for that, user needs to retry again from start
            self.logger("Error while running the job. Please retry by closing everying.", LogType.ERROR)
            raise Exception(str(e))
        
    
    def get_user_registration_metadata(self,page:Page,userName: str, password: str)-> dict:
        """
        Returns the user metadata to the workers
        """
        # print("Runtime manager for user metadata is triggered")
        screening = page.locator('[title="Screening"]')
        # print("started making login;page")
        loginPage = LoginPage(page=page, synchronizer=self.synchronizer, success_locator=screening)
        result = loginPage.get_authenticate_user_response(userName=userName,password=password)
        return result

        
            
        
        




