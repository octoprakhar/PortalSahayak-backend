from dataclasses import dataclass

from constants.job_status import JobStatus
from all_models.InstitutionData import InstitutionData
from all_models.UserRegistrationMetadata import UserRegistrationMetadata

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
    is_anm_present: bool = False
    max_existing_child_without_data: int = 80000

    @classmethod
    def from_dict(cls, data: dict):
        data = data.copy()

        if data.get("institution_data"):
            data["institution_data"] = InstitutionData(**data["institution_data"])

        if isinstance(data.get("status"), str):
            data["status"] = JobStatus(data["status"])

        return cls(**data)