from dataclasses import dataclass
from typing import Optional,Dict

from all_models.UserRegistrationMetadata import UserRegistrationMetadata

@dataclass
class UserMetadata:
    job_id: str
    created_at: str
    username: str
    password: str
    registration_metadata: Optional[UserRegistrationMetadata] = None
    selected_facility: Optional[Dict[str, str]] = None