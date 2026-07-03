from dataclasses import dataclass

from constants.job_status import JobStatus
from all_models.InstitutionData import InstitutionData
from all_models.UserRegistrationMetadata import UserRegistrationMetadata

@dataclass
class JobMetadata:
    job_id: str
    status: JobStatus
    created_at : str
    address: str
    mobile_number: str
    date: str
    uploaded_file: str = "uploaded.csv"
    institution_data : InstitutionData = None

