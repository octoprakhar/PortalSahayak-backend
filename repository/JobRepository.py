from abc import ABC,abstractmethod
from fastapi import UploadFile

from database.model.Job import Job
from all_models.InstitutionData import InstitutionData
from database.model.MetadataForJobCreation import MetadataForJobCreation
from constants.job_status import JobStatus

class JobRepository(ABC):
    """
    This class will help do the job related CRUD operations out there.
    """

    @abstractmethod
    def create(self, job_creation_metadata: MetadataForJobCreation) -> str:
        """
        Creating the job with metadata
        """
        pass

    @abstractmethod
    def upload_institution_data(self, job_id: str, institution_data: InstitutionData) -> str:
        """
        We will get the institution data, then convert it to dict, and then upload it
        """

    @abstractmethod
    def upload_file(self, job_id: str, file: UploadFile) -> str:
        """
        Upload the file you want to work
        """
        pass

    @abstractmethod
    def get_job_by_job_id(self, job_id: str) -> Job:
        """
        Fetch the job with job id, if not return None
        """
        pass

    @abstractmethod
    def get_uploaded_file_url(self,job_id: str, file_path: str) -> str | None:
        """
        Return the uploaded file public url or signed url, so that we can download the file
        it will take that file path and create the url
        """
        pass

    @abstractmethod
    def update_job_status(self, job_id: str,new_status: JobStatus) -> None:
        """
        We will update the job status here
        """

