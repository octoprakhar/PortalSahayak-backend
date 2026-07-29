from pydantic import BaseModel
from typing import Dict

class FacilityMappingRequest(BaseModel):
    selected_facility: Dict[str, str]
    user_id: str