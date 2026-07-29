from dataclasses import dataclass

from typing import Optional,Dict

from constants.job_status import JobStatus
from all_models.ClassRange import ClassRange
from all_models.InstitutionData import InstitutionData

@dataclass
class Job:
    """
    This is the same table like in the job.
    """
    status: JobStatus
    address: str
    mobile_number: str
    planned_date: str
    class_range: ClassRange
    is_anm_present: bool
    existing_limit: int
    user_id: str
    job_id: str
    created_at: str
    upload_file_path: Optional[str] = None
    institution_data: InstitutionData = None
    