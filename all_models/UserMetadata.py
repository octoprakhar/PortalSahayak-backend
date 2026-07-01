from dataclasses import dataclass

@dataclass
class UserMetadata:
    job_id: str
    created_at: str
    username: str
    password: str