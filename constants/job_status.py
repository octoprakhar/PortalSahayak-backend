from enum import Enum

class JobStatus(str, Enum):
    IDLE = "idle"
    WAITING_LOGIN = "waiting_login"
    WAITING_INSTITUTION = "waiting_institution"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"