from dataclasses import dataclass,field
from enum import Enum

class FeedbackOutcome(Enum):
    SUCCESS = "success"
    DUPLICATE = "duplicate"
    VALIDATION_ERROR = "validation_error"
    FAILURE = "failure"
    UNKNOWN = "unknown"
    INVALID_DATA = "invalid_data"
    SYSTEM_ERROR = "system_error"

@dataclass
class FeedbackResult:
    outcome: FeedbackOutcome
    message: str | None = None
    validation_errors : list[str] = field(default_factory=list)