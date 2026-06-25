from enum import Enum

class WorkflowStage(Enum):
    PERSONAL_DETAILS = "personal"
    HEALTH_DETAILS = "health"
    FINAL_SUBMIT = "final_submit"