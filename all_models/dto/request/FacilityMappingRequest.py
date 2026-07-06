from pydantic import BaseModel
from typing import Dict

class FacilityMappingRequest(BaseModel):
    selected_facility: Dict[str, str]
    job_id: str