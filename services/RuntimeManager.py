from playwright.sync_api import Page,sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from constants.job_status import JobStatus
from services.JobManager import JobManager
from all_models.JobLogs import JobLog
from constants.log_type import LogType
from services.ActiveJobStore import ActiveJobStore
from all_models.RuntimeJob import RuntimeJob
from workflow.workflow import ScreeningWorkflow
from all_models.ChildProcessingResult import ChildProcessingResult


class RunTimeManager:
    """
    It handles all the Runtime related things which will be stored in-memory 
    Runtime means when you had created the job, and now the browser instance is opened,
    then storing that instance, page instance, browser instance, and playwright instance for that job , in jobs/active_job.json
    Active job means the jobs which are neither IDLE, COMPLETED, FAILED.
    """

    def __init__(self, job_id: str):
        """
        To initialize it, we need job_id, a job to Run, it must be in JobStatus.IDLE state, that means it has formed and ready to run.
        """
        self.job_id = job_id

    def launch_browser_instance(self) -> RuntimeJob:
        """
        Check correct Status. Only launch instance if it is in IDLE state. else throw error or other things. It will return the page instance.
        and after launching it, it must pause the screen to do the loggin thing. After launching, update the job status to JobStatus.WAITING_LOGIN
        """
        ## Check whether that job is in IDLE state or not.
        status = JobManager.get_current_status(self.job_id)
        if status != JobStatus.IDLE:
            raise ValueError("Cannot launch browser for this job as it is launched once already")
        
        ## Launching the broswer instance, and then storing it in active jobs memory
        p = sync_playwright().start()
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://rbsk.mohfw.gov.in/RBSK/login")

        ActiveJobStore.add_job(job_id=self.job_id, playwright=p,browser=browser,context=context, page=page)
        JobManager.update_job_status(status=JobStatus.WAITING_LOGIN, job_id=self.job_id)
        JobManager.add_log(job_id=self.job_id, log=JobLog(timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),message="Browser opened and login page loaded",type=LogType.SUCCESS))

        return RuntimeJob(playwright=p, browser=browser, context=context,page=page)
            
        



    def start_select_institution_stage(self):
        """
        It will help the user to open the "Select Institution" screen using month which will be of type like this "May 2026".
        Update the job status to JobStataus.WAITING_INSTITUTION
        It returns the same page instance in case it is needed again in different api request. to save it in memory. 
        I don't think in future, user will use in memory cache to give the page instance by intself when api is called, so later it may not 
        be very useful
        """
        runtime_job = ActiveJobStore.get_job(job_id=self.job_id)

        if runtime_job is None:
            raise ValueError(f"Job {self.job_id} not found")
        
        page:Page = runtime_job.page

        screening = page.locator('[title="Screening"]').wait_for(timeout=3000)

        try:
            page.locator('[title="Screening"]').wait_for(
                state="visible",
                timeout=3000
            )
        except Exception:
            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="User is not logged in. Please login and retry.",
                    type=LogType.ERROR
                )
            )
            return

        ## Verify first that user has logged in or not, if not send user an error log of failing and ask for retry

        try:
            month = JobManager.get_screening_month(self.job_id)
        except Exception as e:
            raise RuntimeError(e.message)
        
        page.locator('[title="Screening"]').click()
        page.wait_for_timeout(5000)
        page.locator('[name="financialMonth"]').select_option(label=month)
        page.get_by_role('button',name='Search').click()
        JobManager.add_log(job_id=self.job_id, log=JobLog(timeStamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),message="Successfully opened the institution page, Waiting for user to select institution",type=LogType.SUCCESS))

        ## Update the status
        JobManager.update_job_status(status=JobStatus.WAITING_INSTITUTION,job_id=self.job_id)
        JobManager.add_log(job_id=self.job_id, log=JobLog(timeStamp=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),message="Waiting for user to select the intitution"))
        

    def start_child_screening(self):
        """
        It will Trigger ChildScreening class to start screening, and change the job status to "RUNNING"
        
        """
        ## Check first whether a person has selected the institution by check "Add New Child" Button is present on the screen or not.
        runtime_job = ActiveJobStore.get_job(job_id=self.job_id)

        if runtime_job is None:
            raise ValueError(f"Job {self.job_id} not found")
        
        page:Page = runtime_job.page

        try:
            page.get_by_role('button',name="Add New Child").wait_for(
                state="visible",
                timeout=3000
            )
        except Exception:
            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Institution is not selected please select the institution",
                    type=LogType.ERROR
                )
            )
            return
        
        try:
            
            ## Get the file path of the .csv uploaded
            csv_file = JobManager.get_uploaded_file_path(self.job_id)

            ## Get address and phone number
            metadata = JobManager.get_job_metadata(self.job_id)
            address = metadata.address
            mobileNumber = metadata.mobile_number

            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Got required data.... Starting to run the job",
                    type=LogType.INFO
                )
            )
            JobManager.update_job_status(JobStatus.RUNNING,self.job_id)



        except Exception as e:
            ## Moving to failed as I can't do anything for that, user needs to retry again from start
            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Cannot get required data for the job to start. Please retry again moving the job to failed.",
                    type=LogType.ERROR
                )
            )
            JobManager.update_job_status(JobStatus.FAILED,self.job_id)

            ## TODO Cleanup of job is required
            ## Runtime data
            ActiveJobStore.remove_job(job_id=self.job_id)
            ## Persistant data
            JobManager.clean_job(job_id=self.job_id)
            return

        ## Start Screening Workflow with all the data
        try:
            screeningWorkFLow: ScreeningWorkflow = ScreeningWorkflow(page=page,job_id=self.job_id)
        
            failed_result = screeningWorkFLow.run(csv_file,mobileNumber,address)
            ## TODO change it to csv and then send it to data
            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Completed the JOB Succesfully 🎉🎉🎉🎉.",
                    type=LogType.SUCCESS
                )
            )
            
            ## Put job status as completed
            JobManager.update_job_status(JobStatus.COMPLETED, job_id=self.job_id)

            ## Remove job from active job
            ActiveJobStore.remove_job(job_id=self.job_id)
            

        except Exception as e:
            ## Moving to failed as I can't do anything for that, user needs to retry again from start
            JobManager.add_log(
                job_id=self.job_id,
                log=JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message="Error while running the job. Please retry by closing everying.",
                    type=LogType.ERROR
                )
            )
            JobManager.update_job_status(JobStatus.FAILED,self.job_id)
            ## TODO job cleanup is required
            ## Runtime data
            ActiveJobStore.remove_job(job_id=self.job_id)
            ## Persistant data
            # JobManager.clean_job(job_id=self.job_id)
            return
        

        
            
        
        




