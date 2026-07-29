from dataclasses import dataclass
from typing import Optional,Dict

from all_models.ClassRange import ClassRange
from constants.job_status import JobStatus


@dataclass
class MetadataForJobCreation:
    user_id: str
    status: JobStatus
    address: str
    mobile_number: str
    planned_date: str
    class_range: ClassRange
    is_anm_present: bool
    existing_limit: int
    job_id: Optional[str] = None
    created_at: Optional[str] = None
