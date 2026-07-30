from dataclasses import dataclass

from typing import Optional

@dataclass
class JobReport:
    success_file_remote_path: str
    failure_file_remote_path: str
    user_id: str
    job_id: str
    report_id: Optional[str] = None
    created_at: Optional[str] = None