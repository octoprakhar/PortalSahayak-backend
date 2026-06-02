from constants.job_status import JobStatus
from all_models.JobLogs import JobLog


class JobManager:
    """
    This class helps with doing CRUD operations across a particular job. It only does persistant work
    """
    def __init__(self, address: str, mobileNumber: str):
        
        """
        It will initiate the JobManager class, with given address, mobileNumber, 
        it will by itself create all folders and other things regarding job, because then we can change 
        it later on to deal with persistant.
        """

        self.address = address
        self.mobileNumber = mobileNumber

    def create_job(self) -> str:
        """
        Creating job means saving four different things about the data
        1. Saving uploaded files
        2. Maintaining each job's logs
        3. Maintaining each jobs persistant data, like job_id, status, created_at, address, mobileNumber, uploaded file's data
        NOTE: It only creates the job and set the status to JobStatus.IDLE, to run the job, means JobStatus.WAITING_LOGIN, and then create page 
        and other things, this is not the class it only creates.

        Returns:
        job_id : str
        """
        pass

    @staticmethod
    def update_job_status(status: JobStatus, job_id : str) -> bool:
        """
        It will go search for that specific job with id, and change the status to a different one.
        Made it static coz it could be used without making an instance of the class, because different
        endpoints could call it.
        Parameters:
        1. status: JobStatus = It will take new status that user will give to update 
        2. job_id: str = Current id of the job we are working on.

        Returns:
        bool => To check whether updated or not. Maybe in future could be changed. 
        """
        pass

    @staticmethod
    def get_logs(job_id: str) -> list[JobLog]:
        """
        Return all the logs that are saved for this particular job to return them as a string
        
        Parameter:
        job_id : str => Id of the job you want to get the logs

        Returns:
        list[JobLogs] => ALl the logs, with it's types, message and timestamp
        """
        pass

    @staticmethod
    def add_log(job_id: str, log: JobLog) -> JobLog:
        """
        It will add a log for a particular job
        Parameter:
        job_id: str => ID of the job for which log is entering
        log: JobLog => Give message, timestamp , and the type of log

        Returns:
        Returns that same log, maybe we need to send it back later through websocket(not now) to the UI.
        """
        pass


    @staticmethod
    def clean_job(job_id: str) -> bool:
        """
        It will delete all the data regarding a job, all the logs, metadata(both persistant and in-memory), file.

        Parameter:
        1. job_id : str => ID of the job we wanna delete
        
        Returns:
        bool -> to check whether everything is deleted or not.

        """
        pass