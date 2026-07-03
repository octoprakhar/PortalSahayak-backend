from dataclasses import dataclass

from all_models.UserRegistrationMetadata import UserRegistrationMetadata

@dataclass
class UserMetadata:
    job_id: str
    created_at: str
    username: str
    password: str
    registration_metadata: UserRegistrationMetadata = None