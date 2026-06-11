from enum import Enum

class JobStatus(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    LOGGING_IN = "logging_in"
    WAITING_INSTITUTION = "waiting_institution"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"