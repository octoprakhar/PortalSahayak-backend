from dataclasses import dataclass

from constants.job_status import JobStatus

@dataclass
class JobMetadata:
    job_id: str
    status: JobStatus
    created_at : str
    address: str
    mobile_number: str
    month: str
    uploaded_file: str = "uploaded.csv"
