import uuid
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
from zoneinfo import ZoneInfo
import json
from dataclasses import asdict
import shutil
from typing import Optional

from constants.job_status import JobStatus
from constants.log_type import LogType
from all_models.JobLogs import JobLog
from all_models.JobMetadata import JobMetadata



class JobManager:
    """
    This class helps with doing CRUD operations across a particular job. It only does persistant work
    """
    def __init__(self, address: str, mobileNumber: str, file: UploadFile, month: str):
        
        """
        It will initiate the JobManager class, with given address, mobileNumber, 
        it will by itself create all folders and other things regarding job, because then we can change 
        it later on to deal with persistant.
        """

        self.address = address
        self.mobileNumber = mobileNumber
        self.month = month
        self.file = file

    async def create_job(self) -> str:
        """
        Creating job means saving four different things about the data
        1. Saving uploaded files
        2. Maintaining each job's logs
        3. Maintaining each jobs persistant data, like job_id, status, created_at, address, mobileNumber, uploaded file's data
        
        It only creates the job and set the status to JobStatus.IDLE, to run the job, means JobStatus.WAITING_LOGIN, and then create page 
        and other things, this is not the class it only creates.

        Returns:
        job_id : str
        """

        # Let's start by creating the job id
        job_id = str(uuid.uuid4())

        ## For now let's just make a folder with job_id inside 'jobs' folder and save data there. Afterwards we need to save somewhere else for persistence
        job_dir = Path("jobs") / job_id
        job_dir.mkdir(exist_ok=True, parents=True)

        ## Now save the file in the folder
        try:
            uploaded_file_path = job_dir/ "uploaded.csv"
            file_bytes = await self.file.read()
            with open(uploaded_file_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            raise RuntimeError("Can't create the file that is uploaded by the user") from e

        ## Now making the file to store persistant data regarding job
        job_metadata = JobMetadata(job_id=job_id, status=JobStatus.IDLE.value, created_at=datetime.utcnow().isoformat(), address=self.address, mobile_number=self.mobileNumber,month=self.month)
        with open(job_dir / "job.json", "w", encoding="utf-8") as f:
            json.dump(asdict(job_metadata), f, indent=2)

        ## Now create a log file, with appended log as 'job created', for which I will append a log after that
        self.add_log(job_id=job_id, log=JobLog(timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(), message=f"Created the job with id: {job_id} successfully.", type=LogType.SUCCESS))

        return job_id

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

        ## FOr now go to the file jobs/job_id/job.json, and update the status key 
        try:
            job_file = Path("jobs") / job_id / "job.json"

            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["status"] = status.value

            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            JobManager.add_log(job_id, JobLog(timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),message=f"Updated the Job status of {job_id} to {status}"))

            return True
        except Exception as e:
            raise RuntimeError("Error while updating status") from e

    @staticmethod
    def get_logs(job_id: str, after: Optional[str] = None) -> list[JobLog]:
        """

        Return all the logs that are saved for this particular job and is after a particular time

        

        Parameter:

        job_id : str => Id of the job you want to get the logs
        after: str = Time stamp after which we want the logs



        Returns:

        list[JobLogs] => ALl the logs, with it's types, message and timestamp

        """
        log_file = Path("jobs") / job_id / "logs.jsonl"

        if not log_file.exists():
            return []

        after_dt = None
        if after:
            after_dt = datetime.fromisoformat(after)

        logs: list[JobLog] = []

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                if after_dt:
                    log_dt = datetime.fromisoformat(data["timeStamp"])

                    if log_dt <= after_dt:
                        continue

                logs.append(
                    JobLog(
                        timeStamp=data["timeStamp"],
                        message=data["message"],
                        type=LogType[data["type"]],
                    )
                )

            return logs

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

        ## For now job_dir is this, because we are storing in local storage for now.
        job_dir = Path("jobs") / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        log_data = asdict(log)
        log_data["type"] = log.type.name

        with open(job_dir / "logs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data) + "\n")

        return log
    
    @staticmethod
    def get_current_status(job_id: str) -> JobStatus:
        """
        Returns the current status of the given job.

        Parameters:
        job_id : str
            ID of the job.

        Returns:
        JobStatus
            Current status of the job.
        """

        job_file = Path("jobs") / job_id / "job.json"

        if not job_file.exists():
            raise FileNotFoundError(f"Job {job_id} does not exist")

        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return JobStatus(data["status"])

        except KeyError as e:
            raise RuntimeError(
                f"Status field missing in metadata for job {job_id}"
            ) from e

        except ValueError as e:
            raise RuntimeError(
                f"Invalid status '{data.get('status')}' for job {job_id}"
            ) from e
        

    @staticmethod
    def get_screening_month(job_id: str) -> str:
        """
        Returns the screening month of the given job.

        Parameters:
        job_id : str
            ID of the job.

        Returns:
        str
            Screening month (e.g. "May 2026").
        """

        job_file = Path("jobs") / job_id / "job.json"

        if not job_file.exists():
            raise FileNotFoundError(f"Job {job_id} does not exist")

        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data["month"]

        except KeyError as e:
            raise RuntimeError(
                f"Month field missing in metadata for job {job_id}"
            ) from e


    @staticmethod
    def clean_job(job_id: str) -> bool:
        """
        It will delete all the data regarding a job, all the logs, metadata(both persistant and in-memory), file.

        Parameter:
        1. job_id : str => ID of the job we wanna delete
        
        Returns:
        bool -> to check whether everything is deleted or not.

        NOTE: I need to do in-memory, or runtime cleaning too later on

        """
        job_dir = Path("jobs") / job_id

        if not job_dir.exists():
            return False

        try:
            shutil.rmtree(job_dir)
            return not job_dir.exists()
        except Exception:
            return False