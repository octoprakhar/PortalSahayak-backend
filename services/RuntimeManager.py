from playwright.sync_api import Page

class RunTimeManager:
    """
    It handles all the Runtime related things which will be stored in-memory 
    Runtime means when you had created the job, and now the browser instance is opened,
    then storing that instance, page instance, updating a job status(Personally I am putting it here, rather than JobManager, I think it makes more sense)
    """

    def __init__(self, job_id: str):
        """
        To initialize it, we need job_id, a job to Run, it must be in JobStatus.IDLE state, that means it has formed and ready to run.
        """
        self.job_id = job_id

    def launch_browser_instance(self) -> Page:
        """
        Check correct Status. Only launch instance if it is in IDLE state. else throw error or other things. It will return the page instance.
        and after launching it, it must pause the screen to do the loggin thing. After launching, update the job status to JobStatus.WAITING_LOGIN
        """
        pass

    def start_select_institution_stage(self, page:Page, month: str) -> Page:
        """
        It will help the user to open the "Select Institution" screen using month which will be of type like this "May 2026".
        Update the job status to JobStataus.WAITING_INSTITUTION
        It returns the same page instance in case it is needed again in different api request. to save it in memory. 
        I don't think in future, user will use in memory cache to give the page instance by intself when api is called, so later it may not 
        be very useful
        """
        pass

    def start_child_screening(self, page:Page) -> Page:
        """
        It will Trigger ChildScreening class to start screening, and change the job status to "RUNNING"
        
        """
        pass


