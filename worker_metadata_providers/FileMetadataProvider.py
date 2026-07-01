from worker.MetadataProvider import MetadataProvider
from all_models.WorkerContext import WorkerContext
from all_models.JobMetadata import JobMetadata
from all_models.UserMetadata import UserMetadata
from services.JobManager import JobManager


class FileMetadataProvider(MetadataProvider):

    """
    This class will provide metadata to the worker, if that data exists in file.
    I mean it is used, when worker is performing tasks, whose metadata/context lies 
    locally in the machine.
    """
    
    def get_context(self, job_id) -> WorkerContext:
        try:
            userMetadata: UserMetadata = JobManager.get_user_metadata(job_id=job_id)
            jobMetadata: JobMetadata = JobManager.get_job_metadata(job_id=job_id)
            # file_path = JobManager.get_uploaded_file_path(job_id=job_id)
            
            return WorkerContext(userName=userMetadata.username, password=userMetadata.password, address=jobMetadata.address, mobile_number=jobMetadata.mobile_number, planned_date=jobMetadata.date, uploaded_file_path=jobMetadata.uploaded_file, institution_data=jobMetadata.institution_data)
        except Exception as e:
            raise Exception(str(e))