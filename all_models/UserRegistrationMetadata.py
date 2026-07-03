from dataclasses import dataclass

@dataclass
class UserRegistrationMetadata:
    user_name: str
    district_id: int
    health_block_id: int
    state_id: int
    mht_code: int