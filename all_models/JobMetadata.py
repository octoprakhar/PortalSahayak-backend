from dataclasses import dataclass

from constants.job_status import JobStatus
from all_models.InstitutionData import InstitutionData
from all_models.UserRegistrationMetadata import UserRegistrationMetadata
from all_models.ClassRange import ClassRange

@dataclass
class JobMetadata:
    job_id: str
    status: JobStatus
    created_at: str
    address: str
    mobile_number: str
    date: str
    uploaded_file: str = "uploaded.csv"
    institution_data: InstitutionData = None
    class_range : ClassRange = None
    is_anm_present: bool = False
    existing_limit: int = 999999

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()

        if data.get("institution_data"):
            data["institution_data"] = InstitutionData(**data["institution_data"])
        
        if data.get("class_range"):
            data["class_range"] = ClassRange(**data["class_range"])
        
        if isinstance(data.get("status"), str):
            data["status"] = JobStatus(data["status"])

        return cls(**data)