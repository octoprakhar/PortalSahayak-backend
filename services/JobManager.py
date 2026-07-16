import uuid
from pathlib import Path
import shutil
from datetime import datetime
from fastapi import UploadFile
from zoneinfo import ZoneInfo
import json
from dataclasses import asdict
import shutil
from typing import Optional
import csv
from dataclasses import asdict
from enum import Enum

from constants.job_status import JobStatus
from constants.log_type import LogType
from all_models.JobLogs import JobLog
from all_models.JobMetadata import JobMetadata
from all_models.ChildRunResult import ChildRunResult
from all_models.UserMetadata import UserMetadata
from all_models.InstitutionData import InstitutionData
from all_models.UserRegistrationMetadata import UserRegistrationMetadata
from all_models.FacilityCatalog import FacilityCatalog



class JobManager:
    """
    This class helps with doing CRUD operations across a particular job. It only does persistant work
    """
    def __init__(self):
        
        """
        It will initiate the JobManager class, with given address, mobileNumber, 
        it will by itself create all folders and other things regarding job, because then we can change 
        it later on to deal with persistant.
        """

    @staticmethod
    def json_serializer(obj):
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _load_job_metadata(self, job_id: str) -> JobMetadata:
        path = f"jobs/{job_id}/job.json"

        with open(path, "r") as f:
            data = json.load(f)

        return JobMetadata(**data)
    
    def _save_job_metadata(
        self,
        job_metadata: JobMetadata,
    ):
        path = f"jobs/{job_metadata.job_id}/job.json"

        with open(path, "w") as f:
            json.dump(asdict(job_metadata), f, indent=4, default=JobManager.json_serializer)
    
    def _load_user_metadata(self, job_id: str) -> UserMetadata:
        path = f"jobs/{job_id}/user.json"

        with open(path, "r") as f:
            data = json.load(f)

        return UserMetadata(**data)
    
    def _save_user_metadata(
        self,
        user_metadata: UserMetadata,
    ):
        path = f"jobs/{user_metadata.job_id}/user.json"

        with open(path, "w") as f:
            json.dump(asdict(user_metadata), f, indent=4, default=JobManager.json_serializer)

    
    def construct_job(self) -> str:
        """
        It's sole purpose is to create a job_id, and then create a folder, inside jobs, with that id, and returns that id.
        """
        job_id = str(uuid.uuid4())

        ## Now make job_dir
        job_dir = Path("jobs") / job_id
        job_dir.mkdir(exist_ok=True, parents=True)

        return job_id
    
    def store_user_data(self,job_id:str, username:str, password:str):
        """
        Store user related data like userName, and password.
        """
        user_id = str(uuid.uuid4())
        job_dir = Path("jobs") / job_id
        created_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
        userMetadata = UserMetadata(job_id=job_id, created_at=created_at, username=username, password=password)
        with open(job_dir / "user.json", "w", encoding="utf-8") as f:
            
            json.dump(asdict(userMetadata), f, indent=2,default=JobManager.json_serializer)
        
    def store_job_metadata(self,job_id: str, address: str, mobile_number: str, screening_date: str, is_anm_present: bool = False, max_existing_child_without_data: int = 80000):
        """
        Storing job related metadata in different place
        """
        status = JobStatus.IDLE
        job_dir = Path("jobs") / job_id
        created_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
        jobMetadata = JobMetadata(job_id=job_id, status=status, created_at=created_at, address=address, mobile_number=mobile_number, date=screening_date,is_anm_present=is_anm_present, max_existing_child_without_data=max_existing_child_without_data)
        with open(job_dir / "job.json", "w", encoding="utf-8") as f:
            json.dump(asdict(jobMetadata), f, indent=2,default=JobManager.json_serializer)

    def store_facility_catalog(self, job_id: str, facility_catalog: FacilityCatalog):
        """
        For now store it in the job level, but when DB will be there, we will shift it to user level

        For now store it inside jobs/job_id/catalog.json
        """
        job_dir = Path("jobs") / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        catalog_path = job_dir / "catalog.json"

        with catalog_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(facility_catalog), f, indent=2)

    def get_job_facility_catalog(self, job_id: str) -> FacilityCatalog | None:
        """
        Retrieve the facility catalog for the given job.

        Returns:
            FacilityCatalog if it exists, otherwise None.
        """
        catalog_path = Path("jobs") / job_id / "catalog.json"

        if not catalog_path.exists():
         return None

        with catalog_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return FacilityCatalog(**data)

    def saved_mapped_facility(self,job_id: str, mapped_facility: dict[str,str]):
        """
        It will take mapped facility and store it in user table
        """
        userMetadata = self._load_user_metadata(job_id=job_id)
        userMetadata.selected_facility = mapped_facility
        self._save_user_metadata(user_metadata=userMetadata)


    def upload_file(self,job_id:str, uploaded_file: UploadFile):
        """
        Upload the file to jobs/job_id/uploaded.csv, and also update jobMetadata present in jobs/job_id/job.json, change it to JobMetadata, and append the 
        uplloaded file path, and then save it again
        """
        job_dir = Path("jobs") / job_id

        # Preserve extension
        extension = Path(uploaded_file.filename).suffix
        file_path = job_dir / f"uploaded{extension}"

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

        # Load existing metadata
        job_metadata = self._load_job_metadata(job_id)

        # Update metadata
        job_metadata.uploaded_file = str(file_path)

        # Save metadata
        self._save_job_metadata(job_metadata)

        return str(file_path)

    def upload_institution_data(self,job_id: str,institution_data: InstitutionData):
        """
        Get job_metadata file : jobs/job_id/job.json, change it to jobMetadata type, and edit institutiondata.
        """
        job_metadata = self._load_job_metadata(job_id)

        job_metadata.institution_data = institution_data

        self._save_job_metadata(job_metadata)

    def get_institution_data(self,job_id: str) -> InstitutionData | None:
        """
        Get the data of the user selected institution
        """
        job_metadata = self._load_job_metadata(job_id=job_id)
        if not job_metadata.institution_data:
            return None
        return job_metadata.institution_data
    
    def get_uploaded_file_path(self,job_id: str) -> str | None:
        job_metadata = self._load_job_metadata(job_id)
        if not job_metadata.uploaded_file:
            return None
        
        return job_metadata.uploaded_file


    def upload_user_registration_metadata(self,job_id: str, user_registration_metadata:UserRegistrationMetadata):
        """
        Save registration metadata, of user type
        """
        user_metadata = self._load_user_metadata(job_id=job_id)
        user_metadata.registration_metadata = user_registration_metadata
        self._save_user_metadata(user_metadata=user_metadata)


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
            job_dir = Path("jobs") / job_id
            job_dir.mkdir(parents=True, exist_ok=True)

            job_file = job_dir / "job.json"

            if job_file.exists():
                with open(job_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                metadata = JobMetadata(
                    job_id=job_id,
                    status=status,
                    created_at=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    address="",
                    mobile_number="",
                    date="",
                    uploaded_file="uploaded.csv",
                    institution_data=None,
                )

                data = asdict(metadata)

                # Convert enum to its value
                data["status"] = metadata.status.value

            # Update status
            data["status"] = status.value

            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    indent=2,
                    default=JobManager.json_serializer,
                )

            JobManager.add_log(
                job_id,
                JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message=f"Updated the Job status of {job_id} to {status}",
                ),
            )

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
    def get_uploaded_file_path(job_id: str) -> Path | None:
        """
        Returns uploaded file path, so that we can run the job

        Params: 
        job_id: str => job id whose file you want

        Returns: 
        path: Path = file path of the data
        """
        path = Path("jobs") / job_id / "uploaded.csv"

        if path.exists():
            return path

        return None
    
    @staticmethod
    def get_job_metadata(job_id: str) -> JobMetadata | None:
        """
        This function returns the metadata related to job, so that we can get small things about the jobs

        Params:
        job_id: str => job id of the job you want the metadata of.

        Returns:
        jobMetadata: JobMetadata => All metadata related to the job
        """

        job_file = Path("jobs") / job_id / "job.json"

        if not job_file.exists():
            return None
            # raise FileNotFoundError(f"Job {job_id} does not exist")

        with open(job_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return JobMetadata.from_dict(data)
    
    @staticmethod
    def get_user_metadata(job_id: str) -> UserMetadata:
        """
        This function returns the metadata related to user, so that we can get small things about the jobs

        Params:
        job_id: str => job id of the job you want the metadata of.

        Returns:
        jobMetadata: JobMetadata => All metadata related to the job
        """

        user_file = Path("jobs") / job_id / "user.json"

        if not user_file.exists():
            raise FileNotFoundError(f"Job {job_id} does not exist")

        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return UserMetadata(**data)
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
    def get_screening_date(job_id: str) -> str:
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

            return data["date"]

        except KeyError as e:
            raise RuntimeError(
                f"Month field missing in metadata for job {job_id}"
            ) from e
    
    @staticmethod
    def save_success_and_failure_files(job_id:str,success_rows: list[ChildRunResult], failure_rows : list[ChildRunResult])-> tuple[str,str]:
        """
        It will save persistantly success and failure data for that job in the database. and returns
        success_path, failure_path.

        For now save it in jobs/{job_id}/success.csv,and failure.csv
        """

        job_dir = Path("jobs") / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        success_file = job_dir / "success.csv"
        failure_file = job_dir / "failure.csv"

        def write_csv(file_path: Path, rows: list[ChildRunResult]) -> None:
            if not rows:
                # Create an empty file
                file_path.touch(exist_ok=True)
                return

            row_dicts = [asdict(row) for row in rows]

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=row_dicts[0].keys()
                )
                writer.writeheader()
                writer.writerows(row_dicts)

        try:
            write_csv(success_file, success_rows)
            write_csv(failure_file, failure_rows)

            JobManager.add_log(
                job_id,
                JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message=(
                        f"Saved {len(success_rows)} successful rows and "
                        f"{len(failure_rows)} failed rows."
                    ),
                    type=LogType.SUCCESS,
                ),
            )

            return str(success_file), str(failure_file)

        except Exception as e:
            JobManager.add_log(
                job_id,
                JobLog(
                    timeStamp=datetime.now(
                        ZoneInfo("Asia/Kolkata")
                    ).isoformat(),
                    message=f"Failed to save result files: {str(e)}",
                    type=LogType.ERROR,
                ),
            )
            raise RuntimeError(
                "Failed to save success and failure files"
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