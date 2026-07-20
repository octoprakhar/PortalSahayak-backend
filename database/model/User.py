from dataclasses import dataclass
from datetime import datetime

from typing import Optional,Dict

@dataclass
class User:
    """
    The table same present as in the database, same row is present in database.
    Since data will come in stage wise, so the values which will come in later stages are all just optional
    """
    user_id: str
    created_at: datetime
    user_name: str
    password: str
    doctor_name: Optional[str] = None
    district_id: Optional[int] = None
    health_block_id: Optional[int] = None
    state_id: Optional[int] = None
    mht_code: Optional[int] = None
    selected_facility: Optional[Dict[str,str]] = None
